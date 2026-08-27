from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID
import uuid

from app.core.database import get_db
from app.models import (
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceType,
    MemberRole,
    CostCenter,
    CostCenterScope,
    Category
)
from app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
    WorkspaceResponse,
    WorkspaceDetailResponse,
    MemberResponse,
    MemberInviteRequest,
    MemberUpdateRequest
)
from app.api.deps import get_current_user

router = APIRouter()

async def get_workspace_membership(workspace_id: UUID, user_id: UUID, db: AsyncSession) -> WorkspaceMember:
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id
    )
    membership = (await db.execute(stmt)).scalar_one_or_none()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Você não tem permissão para acessar este workspace.'
        )
    return membership


@router.get('', response_model=list[WorkspaceResponse], summary='Listar Workspaces do Usuário')
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkspaceMember).where(WorkspaceMember.user_id == current_user.id).options(
        selectinload(WorkspaceMember.workspace)
    )
    memberships = (await db.execute(stmt)).scalars().all()
    
    res = []
    for m in memberships:
        w = m.workspace
        res.append(
            WorkspaceResponse(
                id=w.id,
                name=w.name,
                type=w.type,
                owner_id=w.owner_id,
                currency=w.currency,
                created_at=w.created_at,
                role_of_current_user=m.role.value
            )
        )
    return res


@router.post('', response_model=WorkspaceDetailResponse, status_code=status.HTTP_201_CREATED, summary='Criar Novo Workspace')
async def create_workspace(
    req: WorkspaceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = Workspace(
        id=uuid.uuid4(),
        name=req.name.strip(),
        type=req.type,
        owner_id=current_user.id,
        currency=req.currency.upper()
    )
    db.add(workspace)
    await db.flush()

    # Adiciona criador como Owner
    member = WorkspaceMember(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        user_id=current_user.id,
        role=MemberRole.OWNER,
        display_name=current_user.full_name,
        declared_income=0.00
    )
    db.add(member)
    await db.flush()

    # Centros de Custo padrões
    if req.type == WorkspaceType.FAMILY:
        cc_casa = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name='Casa / Moradia', scope=CostCenterScope.HOME)
        cc_familia = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name='Família / Filhos', scope=CostCenterScope.FAMILY)
        cc_casal = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name='Casal', scope=CostCenterScope.COUPLE)
        cc_pessoal = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name=f'Pessoal ({current_user.full_name.split()[0]})', scope=CostCenterScope.INDIVIDUAL, assigned_member_id=member.id)
        db.add_all([cc_casa, cc_familia, cc_casal, cc_pessoal])
    else:
        cc_pessoal = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name='Pessoal', scope=CostCenterScope.INDIVIDUAL, assigned_member_id=member.id)
        cc_casa = CostCenter(id=uuid.uuid4(), workspace_id=workspace.id, name='Casa / Moradia', scope=CostCenterScope.HOME, assigned_member_id=member.id)
        db.add_all([cc_pessoal, cc_casa])

    # Categorias padrões
    cats = [
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Alimentação', icon='utensils', color='#10B981'),
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Moradia', icon='home', color='#3B82F6'),
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Transporte', icon='car', color='#F59E0B'),
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Saúde', icon='heart-pulse', color='#EF4444'),
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Lazer & Conforto', icon='sparkles', color='#8B5CF6'),
        Category(id=uuid.uuid4(), workspace_id=workspace.id, name='Receitas', icon='trending-up', color='#00D084'),
    ]
    db.add_all(cats)
    await db.commit()

    return WorkspaceDetailResponse(
        id=workspace.id,
        name=workspace.name,
        type=workspace.type,
        owner_id=workspace.owner_id,
        currency=workspace.currency,
        created_at=workspace.created_at,
        role_of_current_user=MemberRole.OWNER.value,
        members=[
            MemberResponse(
                id=member.id,
                user_id=current_user.id,
                email=current_user.email,
                display_name=member.display_name,
                role=member.role,
                declared_income=member.declared_income,
                custom_split_percentage=member.custom_split_percentage,
                joined_at=member.joined_at
            )
        ]
    )


@router.get('/{workspace_id}', response_model=WorkspaceDetailResponse, summary='Detalhes do Workspace')
async def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    membership = await get_workspace_membership(workspace_id, current_user.id, db)
    
    stmt = select(Workspace).where(Workspace.id == workspace_id).options(
        selectinload(Workspace.members).selectinload(WorkspaceMember.user)
    )
    workspace = (await db.execute(stmt)).scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Workspace não encontrado.')

    members_list = []
    for m in workspace.members:
        members_list.append(
            MemberResponse(
                id=m.id,
                user_id=m.user_id,
                email=m.user.email if m.user else None,
                display_name=m.display_name,
                role=m.role,
                declared_income=m.declared_income,
                custom_split_percentage=m.custom_split_percentage,
                joined_at=m.joined_at
            )
        )

    return WorkspaceDetailResponse(
        id=workspace.id,
        name=workspace.name,
        type=workspace.type,
        owner_id=workspace.owner_id,
        currency=workspace.currency,
        created_at=workspace.created_at,
        role_of_current_user=membership.role.value,
        members=members_list
    )


@router.put('/{workspace_id}', response_model=WorkspaceResponse, summary='Editar Workspace')
async def update_workspace(
    workspace_id: UUID,
    req: WorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    membership = await get_workspace_membership(workspace_id, current_user.id, db)
    if membership.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Apenas administradores podem editar o workspace.')

    stmt = select(Workspace).where(Workspace.id == workspace_id)
    workspace = (await db.execute(stmt)).scalar_one_or_none()

    if req.name:
        workspace.name = req.name.strip()
    if req.currency:
        workspace.currency = req.currency.upper()

    await db.commit()
    await db.refresh(workspace)

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        type=workspace.type,
        owner_id=workspace.owner_id,
        currency=workspace.currency,
        created_at=workspace.created_at,
        role_of_current_user=membership.role.value
    )


@router.post('/{workspace_id}/members', response_model=MemberResponse, status_code=status.HTTP_201_CREATED, summary='Adicionar / Convidar Membro')
async def add_member(
    workspace_id: UUID,
    req: MemberInviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    membership = await get_workspace_membership(workspace_id, current_user.id, db)
    if membership.role not in [MemberRole.OWNER, MemberRole.ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Apenas administradores podem convidar membros.')

    # Localiza ou valida usuário
    stmt = select(User).where(User.email == req.email.lower().strip())
    target_user = (await db.execute(stmt)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Nenhum usuário encontrado com o e-mail {req.email}. Peça para o usuário criar uma conta no KIVO primeiro.'
        )

    # Verifica se já é membro
    stmt_check = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == target_user.id
    )
    if (await db.execute(stmt_check)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Este usuário já é membro deste workspace.')

    new_member = WorkspaceMember(
        id=uuid.uuid4(),
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=req.role,
        display_name=req.display_name.strip(),
        declared_income=req.declared_income,
        custom_split_percentage=req.custom_split_percentage
    )
    db.add(new_member)
    await db.flush()
    
    # Se for workspace Família, cria também um Centro de Custo pessoal para o novo membro
    stmt_ws = select(Workspace).where(Workspace.id == workspace_id)
    ws = (await db.execute(stmt_ws)).scalar_one()
    if ws.type == WorkspaceType.FAMILY:
        cc_novo = CostCenter(
            id=uuid.uuid4(),
            workspace_id=workspace_id,
            name=f'Pessoal ({req.display_name.split()[0]})',
            scope=CostCenterScope.INDIVIDUAL,
            assigned_member_id=new_member.id
        )
        db.add(cc_novo)

    await db.commit()
    await db.refresh(new_member)

    return MemberResponse(
        id=new_member.id,
        user_id=target_user.id,
        email=target_user.email,
        display_name=new_member.display_name,
        role=new_member.role,
        declared_income=new_member.declared_income,
        custom_split_percentage=new_member.custom_split_percentage,
        joined_at=new_member.joined_at
    )


@router.put('/{workspace_id}/members/{member_id}', response_model=MemberResponse, summary='Atualizar Dados do Membro')
async def update_member(
    workspace_id: UUID,
    member_id: UUID,
    req: MemberUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_membership = await get_workspace_membership(workspace_id, current_user.id, db)
    
    stmt = select(WorkspaceMember).where(
        WorkspaceMember.id == member_id,
        WorkspaceMember.workspace_id == workspace_id
    ).options(selectinload(WorkspaceMember.user))
    member = (await db.execute(stmt)).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Membro não encontrado.')

    # Apenas o próprio membro ou Admin/Owner pode alterar
    is_self = (member.user_id == current_user.id)
    is_admin = current_membership.role in [MemberRole.OWNER, MemberRole.ADMIN]
    
    if not (is_self or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Sem permissão para alterar este membro.')

    if req.display_name:
        member.display_name = req.display_name.strip()
    if req.declared_income is not None:
        member.declared_income = req.declared_income
    if req.custom_split_percentage is not None:
        member.custom_split_percentage = req.custom_split_percentage
    if req.role and is_admin and not is_self: # Apenas admin altera role de outros
        member.role = req.role

    await db.commit()
    await db.refresh(member)

    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=member.user.email if member.user else None,
        display_name=member.display_name,
        role=member.role,
        declared_income=member.declared_income,
        custom_split_percentage=member.custom_split_percentage,
        joined_at=member.joined_at
    )
