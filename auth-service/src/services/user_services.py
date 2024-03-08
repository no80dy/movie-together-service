import json
import logging
import string
import uuid
from datetime import datetime
from functools import lru_cache
from secrets import choice as secrets_choice

from db.postgres import get_session
from db.redis import RedisStorage
from db.storage import TokenHandler, get_nosql_storage
from fastapi import Depends
from models.entity import (
    RefreshSession,
    User,
    UserLoginHistory,
    UserSocialNetwork,
)
from schemas.entity import (
    RefreshDelDb,
    RefreshToDb,
    UserCreate,
    UserLoginHistoryInDb,
    UserLogoutHistoryInDb,
    UserSocialNetworkInDb,
)
from sqlalchemy import UUID, and_, delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash, generate_password_hash

CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min
YANDEX_SOCIAL_NAME = "yandex"


class UserService:
    def __init__(
        self,
        token_handler: TokenHandler,
        db: AsyncSession,
    ) -> None:
        self.token_handler = token_handler
        self.db = db

    async def get_user_by_user_id(self, user_id) -> User:
        user = (
            await self.db.execute(select(User).where(User.id == user_id))
        ).scalar()
        return user

    async def get_user_groups_permissions(self, user_id: str) -> list[dict]:
        user = (
            await self.db.execute(select(User).where(User.id == user_id))
        ).scalar()

        groups_permissions = []
        for group in user.groups:
            groups_permissions.append(
                {
                    "group": group.group_name,
                    "permissions": [
                        permission.permission_name
                        for permission in group.permissions
                    ],
                }
            )
        return groups_permissions

    async def check_exist_user(self, user_dto):
        result = await self.db.execute(
            select(User).where(User.username == user_dto.get("username"))
        )
        user = result.scalars().first()

        return bool(user)

    async def check_unique_email(self, user_dto):
        result = await self.db.execute(
            select(User).where(User.email == user_dto.get("email"))
        )
        user = result.scalars().first()

        return True if not user else False

    async def create_user(self, user_dto):
        user = User(**user_dto)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_password(self, user_dto):
        user = User(**user_dto)
        if (
            not await self.check_repeated_password(
                user_dto.get("password"), user_dto.get("repeated_old_password")
            )
            or not await self._check_old_password(user_dto)
            or user_dto.get("password")
            == user_dto.get(
                "new_password"
            )  # старый и новый пароль должны отличаться
        ):
            return False

        new_password = generate_password_hash(user_dto.get("new_password"))
        await self.db.execute(
            update(User)
            .where(User.username == user_dto.get("username"))
            .values(password=new_password),
        )
        await self.db.commit()

        return user

    async def check_repeated_password(self, password, repeated_password):
        if not password == repeated_password:
            return False
        return True

    async def _check_old_password(self, user_dto):
        result = await self.db.execute(
            select(User).where(User.username == user_dto.get("username"))
        )
        user = result.scalars().first()
        old_pass_verified = check_password_hash(
            user.password, user_dto.get("password")
        )

        return True if old_pass_verified else False

    async def get_user_by_username(self, username: str) -> User | None:
        """Возвращает пользователя из базы данных по его username, если он есть."""
        try:
            result = await self.db.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            logging.error(e)

    async def get_user_by_email(self, email: str) -> User | None:
        """Возвращает пользователя из базы данных по его email, если он есть."""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            logging.error(e)

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Возвращает пользователя из базы данных по его id, если он есть."""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            logging.error(e)

    async def put_refresh_session_in_db(
        self, user_id: str, user_agent: str, decrypted_token: dict
    ) -> None:
        """Записывает созданный refresh токен в базу данных."""
        session_dto = json.dumps(
            {
                "user_id": user_id,
                "refresh_jti": decrypted_token["jti"],
                "user_agent": user_agent,
                "expired_at": datetime.fromtimestamp(
                    decrypted_token["exp"]
                ).isoformat(),
                "is_active": True,
            }
        )
        data = RefreshToDb.model_validate_json(session_dto)
        try:
            row = RefreshSession(**data.model_dump())
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def check_if_session_exist(
        self, user_id: str, user_agent: str
    ) -> bool:
        """Проверяет существование сессии."""
        session_dto = json.dumps(
            {
                "user_id": user_id,
                "user_agent": user_agent,
            }
        )
        data = RefreshDelDb.model_validate_json(session_dto)
        try:
            stmt = select(RefreshSession).where(
                User.id == data.user_id,
                RefreshSession.user_agent == data.user_agent,
                RefreshSession.is_active.is_(True),
            )
            result = await self.db.execute(stmt)
            row = result.scalars().first()
            return True if row else False
        except SQLAlchemyError as e:
            logging.error(e)

    async def del_refresh_session_in_db(
        self, user_id: str, user_agent: str
    ) -> None:
        """Помечает refresh токен как удаленный в базе данных."""
        session_dto = json.dumps(
            {
                "user_id": user_id,
                "user_agent": user_agent,
            }
        )
        data = RefreshDelDb.model_validate_json(session_dto)
        try:
            stmt = (
                update(RefreshSession)
                .values(is_active=False)
                .where(
                    User.id == data.user_id,
                    RefreshSession.user_agent == data.user_agent,
                    RefreshSession.is_active.is_(True),
                )
            )
            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def del_all_refresh_sessions_in_db(self, user: User) -> None:
        try:
            await self.db.execute(
                update(RefreshSession)
                .where(RefreshSession.user_id == user.id)
                .values(is_active=False),
            )
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)

    async def put_login_history_in_db(
        self, user_id: str, user_agent: str
    ) -> None:
        """Записывает историю входа в аккаунт в базу данных."""
        history_dto = json.dumps(
            {
                "user_id": user_id,
                "user_agent": user_agent,
            }
        )
        data = UserLoginHistoryInDb.model_validate_json(history_dto)
        try:
            row = UserLoginHistory(**data.model_dump())
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def check_unexpected_refresh_token_freshness(
        self, user_id: str, user_agent: str
    ):
        now = datetime.now()
        formatted_datetime = now.replace(microsecond=0)
        result = (
            (
                await self.db.execute(
                    select(RefreshSession).where(
                        and_(
                            RefreshSession.user_id == user_id,
                            RefreshSession.user_agent == user_agent,
                            RefreshSession.expired_at < formatted_datetime,
                            RefreshSession.is_active.is_(True),
                        )
                    )
                )
            )
            .scalars()
            .first()
        )
        return result

    async def check_if_user_login(self, user_id: str, user_agent: str) -> bool:
        """Проверяет существования активной записи о входе пользователя с данного устройства."""
        try:
            stmt = select(UserLoginHistory).where(
                UserLoginHistory.user_id == user_id,
                UserLoginHistory.user_agent == user_agent,
                UserLoginHistory.logout_at.is_(None),
            )

            result = await self.db.execute(stmt)
            active_login_history = result.scalars().first()

            return True if active_login_history else False
        except SQLAlchemyError as e:
            logging.error(e)

    async def put_logout_history_in_db(
        self, user_id: str, user_agent: str
    ) -> None:
        """Записывает историю выхода из аккаунта в базу данных."""
        history_dto = json.dumps(
            {
                "user_id": user_id,
                "user_agent": user_agent,
                "logout_at": datetime.now().isoformat(),
            }
        )
        data = UserLogoutHistoryInDb.model_validate_json(history_dto)
        try:
            stmt = (
                update(UserLoginHistory)
                .values(logout_at=data.logout_at)
                .where(
                    User.id == data.user_id,
                    UserLoginHistory.user_agent == data.user_agent,
                )
            )

            await self.db.execute(stmt)
            await self.db.commit()
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def count_refresh_sessions(self, user_id: str) -> int:
        """Возвращает число открытых сессий пользователя."""
        try:
            result = await self.db.execute(
                select(RefreshSession).where(
                    RefreshSession.user_id == user_id,
                    RefreshSession.is_active.is_(True),
                )
            )
            sessions = result.scalars().all()
            return len(sessions)
        except SQLAlchemyError as e:
            logging.error(e)

    async def calc_previous_and_next_pages(
        self, page_number, page_size, count
    ):
        previous = page_number - 1 if page_number != 1 else None
        next_page = (
            page_number + 1 if count // (page_size * page_number) > 1 else None
        )
        return previous, next_page

    async def get_login_history(
        self,
        user_id: uuid,
        page_size: int,
        page_number: int,
    ) -> list[dict[str, UUID | datetime | str]]:
        offset_min, offset_max = await self.calculate_offset(
            page_size, page_number
        )

        result = await self.db.execute(
            select(UserLoginHistory)
            .where(UserLoginHistory.user_id == str(user_id))
            .order_by(UserLoginHistory.id)
            .offset(offset_min)
            .limit(offset_max - offset_min)
        )
        history = result.scalars().all()

        history_dto = [
            {
                "user_id": item.user_id,
                "user_agent": item.user_agent,
                "login_at": item.login_at,
            }
            for item in history
        ]

        return history_dto

    async def get_login_history_count(self, user_id: uuid):
        result = await self.db.execute(
            select(func.count(UserLoginHistory.id)).where(
                UserLoginHistory.user_id == str(user_id)
            )
        )
        return result.scalar()

    async def calculate_offset(
        self, page_size: int, page_number: int
    ) -> tuple[int, int]:
        offset_min = (page_number - 1) * page_size
        offset_max = offset_min + page_size

        return offset_min, offset_max

    async def check_if_social_exist(
        self, social_name: str, social_id: str
    ) -> User | None:
        """Проверяет существование аккаунта в базе данных на основе id пользователя в социальной сети."""
        try:
            stmt = select(UserSocialNetwork).where(
                and_(
                    UserSocialNetwork.social_name == social_name,
                    UserSocialNetwork.social_id == social_id,
                )
            )
            result = await self.db.execute(stmt)
            account_exist = result.scalars().first()
            if not account_exist:
                return None
            return await self.get_user_by_id(account_exist.user_id)
        except SQLAlchemyError as e:
            logging.error(e)

    @staticmethod
    def _generate_random_password() -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets_choice(alphabet) for _ in range(16))

    async def create_user_social(
        self, social_name: str, social_user: dict
    ) -> User:
        """Создает аккаунт пользователя на основе данных социальной сети."""
        random_password = self._generate_random_password()

        if social_name == YANDEX_SOCIAL_NAME:
            user_dto = json.dumps(
                {
                    "username": social_user["login"],
                    "password": random_password,
                    "repeated_password": random_password,
                    "first_name": social_user["first_name"],
                    "last_name": social_user["last_name"],
                    "email": social_user["default_email"],
                }
            )
        else:
            raise ValueError(f"Unknown social name {social_name}")

        data = UserCreate.model_validate_json(user_dto)
        user = User(**data.model_dump())
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()
        return user

    async def add_user_social(
        self, user_id: UUID, social_name: str, social_user: dict
    ) -> None:
        """Привязывает аккаунт социальной сети к аккаунту пользователя."""
        if social_name == YANDEX_SOCIAL_NAME:
            social_user_dto = json.dumps(
                {
                    "user_id": str(user_id),
                    "social_id": social_user["id"],
                    "social_name": social_name,
                    "social_username": social_user["login"],
                    "social_email": social_user["default_email"],
                }
            )
        else:
            raise ValueError(f"Unknown social name {social_name}")

        data = UserSocialNetworkInDb.model_validate_json(social_user_dto)
        try:
            row = UserSocialNetwork(**data.model_dump())
            self.db.add(row)
            await self.db.commit()
            await self.db.refresh(row)
        except SQLAlchemyError as e:
            logging.error(e)
            await self.db.rollback()

    async def del_user_social(self, social_name: str, social_id: str) -> None:
        """Отвязывает аккаунт социальной сети от аккаунта пользователя."""
        if social_name == YANDEX_SOCIAL_NAME:
            try:
                stmt = delete(UserSocialNetwork).where(
                    UserSocialNetwork.social_name == social_name,
                    UserSocialNetwork.social_id == social_id,
                )
                await self.db.execute(stmt)
                await self.db.commit()
            except SQLAlchemyError as e:
                logging.error(e)
                await self.db.rollback()
        else:
            raise ValueError(f"Unknown social name {social_name}")


@lru_cache()
def get_user_service(
    no_sql: RedisStorage = Depends(get_nosql_storage),
    db: AsyncSession = Depends(get_session),
) -> UserService:
    token_handler = TokenHandler(no_sql, CACHE_EXPIRE_IN_SECONDS)

    return UserService(token_handler, db)
