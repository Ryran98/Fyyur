"""empty message

Revision ID: 13cb38a653f6
Revises: 2c6970a4c75d
Create Date: 2021-04-13 23:40:32.506284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13cb38a653f6'
down_revision = '2c6970a4c75d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=300), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    # ### end Alembic commands ###
