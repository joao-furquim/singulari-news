"""Interface for user and authentication service.

Defines the business-logic contract for user registration, login, password
management, profile updates, and admin operations such as inviting users or
changing roles.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import UserRole
from app.schemas.auth import ForgotPasswordIn, LoginIn, ResetPasswordIn, TokenOut
from app.schemas.user import UserCreateIn, UserInviteIn, UserOut, UserUpdateIn


class IUserService(ABC):
    """Abstract base class defining the user and auth business-logic contract."""

    @abstractmethod
    async def register(self, user_data: UserCreateIn) -> UserOut:
        """Register a new user account with the default ``user`` role.

        :param user_data: Name, email, and plaintext password for the new account.
        :return: The created user serialised as ``UserOut``.
        :raises HTTPException 409: When the email address is already registered.
        """

    @abstractmethod
    async def invite(self, user_data: UserInviteIn) -> UserOut:
        """Create a new user account via admin invitation.

        The created account has ``must_change_password=True`` so the user is
        prompted to set their own password on first login.

        :param user_data: Name, email, initial password, and desired role.
        :return: The created user serialised as ``UserOut``.
        :raises HTTPException 403: When attempting to assign the ``root`` role.
        :raises HTTPException 409: When the email address is already registered.
        """

    @abstractmethod
    async def login(self, credentials: LoginIn) -> TokenOut:
        """Authenticate a user and issue a JWT access token.

        :param credentials: Email and plaintext password.
        :return: A ``TokenOut`` containing the access token, user details,
                 and the user's category preference IDs.
        :raises HTTPException 401: When the email or password is incorrect.
        """

    @abstractmethod
    async def forgot_password(self, data: ForgotPasswordIn) -> None:
        """Initiate a password-reset flow by sending a reset email.

        Silently ignores requests for unregistered emails to prevent
        user-enumeration attacks.

        :param data: The email address for which a reset is requested.
        """

    @abstractmethod
    async def reset_password(self, data: ResetPasswordIn) -> None:
        """Complete a password-reset flow using a previously issued token.

        Marks the token as used after a successful password update.

        :param data: Reset token and the new plaintext password.
        :raises HTTPException 400: When the token is invalid, expired, or already used.
        """

    @abstractmethod
    async def update_profile(self, user_id: UUID, data: UserUpdateIn) -> UserOut:
        """Update the authenticated user's profile fields.

        :param user_id: UUID of the user to update.
        :param data: Fields to patch; ``None`` values are ignored.
        :return: The updated user serialised as ``UserOut``.
        """

    @abstractmethod
    async def list_users(
        self, page: int = 1, limit: int = 10
    ) -> tuple[list[UserOut], int]:
        """Retrieve a paginated list of all non-root users.

        :param page: 1-based page number.
        :param limit: Maximum number of users per page.
        :return: A tuple of ``(users, total_count)``.
        """

    @abstractmethod
    async def delete_user(self, user_id: UUID) -> None:
        """Permanently delete a user account.

        :param user_id: UUID of the user to delete.
        :raises HTTPException 403: When attempting to delete the root user.
        :raises HTTPException 404: When no user with ``user_id`` exists.
        """

    @abstractmethod
    async def update_user_role(self, user_id: UUID, role: UserRole) -> UserOut:
        """Change the role of an existing user.

        :param user_id: UUID of the user whose role should be changed.
        :param role: New role to assign.
        :return: The updated user serialised as ``UserOut``.
        :raises HTTPException 403: When assigning or overwriting the ``root`` role.
        :raises HTTPException 404: When no user with ``user_id`` exists.
        """

    @abstractmethod
    async def change_password(self, user_id: UUID, new_password: str) -> None:
        """Update the user's password and clear the ``must_change_password`` flag.

        :param user_id: UUID of the user whose password to update.
        :param new_password: New plaintext password (will be hashed before storage).
        """
