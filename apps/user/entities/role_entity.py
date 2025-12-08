from enum import Enum

class UserRoleEntity(str, Enum):
    OWNER = "Owner"
    CUSTOMER = "Customer"