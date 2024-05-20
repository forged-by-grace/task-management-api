from enum import Enum

class AccountRoleEnum(str, Enum):
    admin = 'Admin'
    guest = 'Guest'
    user = 'User'
