"""initial

Revision ID: 001
Revises: 
Create Date: 2024-03-20 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 创建工地分组表
    op.create_table(
        'site_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.String(50), unique=True, nullable=False),
        sa.Column('group_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建摄像头表
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.String(50), unique=True, nullable=False),
        sa.Column('camera_name', sa.String(100), nullable=False),
        sa.Column('group_id', sa.String(50), nullable=False),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20)),
        sa.Column('description', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['site_groups.group_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建场景关联表
    op.create_table(
        'camera_scenes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.String(50), nullable=False),
        sa.Column('scene_id', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.camera_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建隐患记录表
    op.create_table(
        'hazards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.String(50), unique=True, nullable=False),
        sa.Column('camera_id', sa.String(50), nullable=False),
        sa.Column('scene_id', sa.String(50), nullable=False),
        sa.Column('location', sa.String(200)),
        sa.Column('violation_type', sa.String(100), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20)),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.camera_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建隐患跟踪表
    op.create_table(
        'hazard_tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('details', sa.Text()),
        sa.Column('tracked_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hazard_id'], ['hazards.hazard_id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('hazard_tracks')
    op.drop_table('hazards')
    op.drop_table('camera_scenes')
    op.drop_table('cameras')
    op.drop_table('site_groups') 