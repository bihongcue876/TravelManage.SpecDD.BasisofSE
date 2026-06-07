"""
依赖注入：角色校验中间件
"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models import User, Role
from auth import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """从 JWT Token 获取当前用户。若 auto_error=False 且无 token，返回 401。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user_id: int = int(sub)
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(*roles: Role):
    """返回一个依赖，要求当前用户拥有指定的角色之一。"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' not permitted. Required: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker


# ── 权限标签系统 ──
# 三角色：admin / frontdesk / finance

_PERMISSION_MAP: dict[str, set[Role]] = {
    "admin":              {Role.ADMIN},                        # 用户管理
    "dashboard:finance":   {Role.FINANCE, Role.ADMIN},         # 财务面板
    "group:manage":        {Role.ADMIN},                       # 管理旅游团
    "route:manage":        {Role.ADMIN},                       # 管理路线
    "task:manage":         {Role.FINANCE, Role.ADMIN},         # 催款与报表
    "application:create":  {Role.FRONTDESK, Role.ADMIN},       # 创建申请
    "application:read":    {Role.FRONTDESK, Role.ADMIN},
    "group:read":          {Role.FRONTDESK, Role.ADMIN},
}


def require_permission(permission: str):
    """权限检查依赖：按角色-权限映射表判断当前用户是否有权。"""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        allowed = _PERMISSION_MAP.get(permission, set())
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: '{permission}' for role '{current_user.role.value}'",
            )
        return current_user
    return checker


def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """可选获取当前用户（无 token 时不报错）。"""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    user_id: int = int(sub)
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()
