from typing import List, Optional

from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Computed, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, Text, Uuid, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import uuid

class Base(DeclarativeBase):
    pass


class PrismaMigrations(Base):
    __tablename__ = '_prisma_migrations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='_prisma_migrations_pkey'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    checksum: Mapped[str] = mapped_column(String(64))
    migration_name: Mapped[str] = mapped_column(String(255))
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    applied_steps_count: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    logs: Mapped[Optional[str]] = mapped_column(Text)
    rolled_back_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class Organisations(Base):
    __tablename__ = 'organisations'
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['organisations.id'], ondelete='SET NULL', onupdate='CASCADE', name='organisations_parent_id_fkey'),
        PrimaryKeyConstraint('id', name='organisations_pkey')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[str]] = mapped_column(Text)

    parent: Mapped[Optional['Organisations']] = relationship('Organisations', remote_side=[id], back_populates='parent_reverse')
    parent_reverse: Mapped[List['Organisations']] = relationship('Organisations', remote_side=[parent_id], back_populates='parent')
    tags: Mapped[List['Tags']] = relationship('Tags', back_populates='org')
    user_orgs: Mapped[List['UserOrgs']] = relationship('UserOrgs', back_populates='org')
    wards: Mapped[List['Wards']] = relationship('Wards', back_populates='org')
    patients: Mapped[List['Patients']] = relationship('Patients', back_populates='org')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('users_email_key', 'email', unique=True)
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    email: Mapped[str] = mapped_column(CITEXT)
    terms_accepted: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    given_names: Mapped[Optional[str]] = mapped_column(Text)
    family_name: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[Optional[str]] = mapped_column(Text, Computed("lower(((COALESCE(given_names, ''::text) || ' '::text) || COALESCE(family_name, ''::text)))", persisted=True))

    user_orgs: Mapped[List['UserOrgs']] = relationship('UserOrgs', back_populates='user')
    patients: Mapped[List['Patients']] = relationship('Patients', back_populates='users')
    abc_submissions: Mapped[List['AbcSubmissions']] = relationship('AbcSubmissions', foreign_keys='[AbcSubmissions.created_by]', back_populates='users')
    abc_submissions_: Mapped[List['AbcSubmissions']] = relationship('AbcSubmissions', foreign_keys='[AbcSubmissions.last_updated_by]', back_populates='users_')
    abs_submissions: Mapped[List['AbsSubmissions']] = relationship('AbsSubmissions', foreign_keys='[AbsSubmissions.created_by]', back_populates='users')
    abs_submissions_: Mapped[List['AbsSubmissions']] = relationship('AbsSubmissions', foreign_keys='[AbsSubmissions.last_updated_by]', back_populates='users_')
    care_tips: Mapped[List['CareTips']] = relationship('CareTips', foreign_keys='[CareTips.created_by]', back_populates='users')
    care_tips_: Mapped[List['CareTips']] = relationship('CareTips', foreign_keys='[CareTips.modified_by]', back_populates='users_')
    care_tip: Mapped[List['CareTips']] = relationship('CareTips', secondary='care_tip_likes', back_populates='user')
    care_tips_history: Mapped[List['CareTipsHistory']] = relationship('CareTipsHistory', back_populates='users')
    key_events: Mapped[List['KeyEvents']] = relationship('KeyEvents', back_populates='users')
    oasmnr_submissions: Mapped[List['OasmnrSubmissions']] = relationship('OasmnrSubmissions', foreign_keys='[OasmnrSubmissions.created_by]', back_populates='users')
    oasmnr_submissions_: Mapped[List['OasmnrSubmissions']] = relationship('OasmnrSubmissions', foreign_keys='[OasmnrSubmissions.last_updated_by]', back_populates='users_')
    patient_bookmarks: Mapped[List['PatientBookmarks']] = relationship('PatientBookmarks', back_populates='user')
    patient_history: Mapped[List['PatientHistory']] = relationship('PatientHistory', back_populates='users')
    abc_history: Mapped[List['AbcHistory']] = relationship('AbcHistory', back_populates='users')
    abs_history: Mapped[List['AbsHistory']] = relationship('AbsHistory', back_populates='users')
    oasmnr_history: Mapped[List['OasmnrHistory']] = relationship('OasmnrHistory', back_populates='users')


class Tags(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organisations.id'], ondelete='RESTRICT', onupdate='CASCADE', name='tags_org_id_fkey'),
        PrimaryKeyConstraint('id', name='tags_pkey'),
        Index('tags_name_org_id_key', 'name', 'org_id', unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(Text)
    org_id: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))

    org: Mapped['Organisations'] = relationship('Organisations', back_populates='tags')
    patient: Mapped[List['Patients']] = relationship('Patients', secondary='patient_tags', back_populates='tag')


class UserOrgs(Base):
    __tablename__ = 'user_orgs'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organisations.id'], ondelete='RESTRICT', onupdate='CASCADE', name='user_orgs_org_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='user_orgs_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'org_id', name='user_orgs_pkey')
    )

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    org_id: Mapped[str] = mapped_column(Text, primary_key=True)
    roles: Mapped[Optional[list]] = mapped_column(ARRAY(Text()), server_default=text('ARRAY[]::text[]'))

    org: Mapped['Organisations'] = relationship('Organisations', back_populates='user_orgs')
    user: Mapped['Users'] = relationship('Users', back_populates='user_orgs')


class Wards(Base):
    __tablename__ = 'wards'
    __table_args__ = (
        ForeignKeyConstraint(['org_id'], ['organisations.id'], ondelete='RESTRICT', onupdate='CASCADE', name='wards_org_id_fkey'),
        PrimaryKeyConstraint('id', name='wards_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(Text)
    org_id: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))

    org: Mapped['Organisations'] = relationship('Organisations', back_populates='wards')
    patients: Mapped[List['Patients']] = relationship('Patients', back_populates='ward')


class Patients(Base):
    __tablename__ = 'patients'
    __table_args__ = (
        ForeignKeyConstraint(['modified_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patients_modified_by_fkey'),
        ForeignKeyConstraint(['org_id'], ['organisations.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patients_org_id_fkey'),
        ForeignKeyConstraint(['ward_id'], ['wards.id'], ondelete='SET NULL', onupdate='CASCADE', name='patients_ward_id_fkey'),
        PrimaryKeyConstraint('id', name='patients_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    given_names: Mapped[str] = mapped_column(Text)
    family_name: Mapped[str] = mapped_column(Text)
    gender: Mapped[str] = mapped_column(Enum('FEMALE', 'MALE', 'NONBINARY', 'OTHER', 'UNKNOWN', 'UNSTATED', name='Genders'))
    date_of_birth: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DISCHARGED', 'DELETED', name='PatientStatus'), server_default=text('\'ACTIVE\'::"PatientStatus"'))
    org_id: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    modified_by: Mapped[str] = mapped_column(Text)
    national_id: Mapped[Optional[str]] = mapped_column(Text)
    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    hospital_patient_id: Mapped[Optional[str]] = mapped_column(Text)
    about: Mapped[Optional[str]] = mapped_column(Text)
    full_name: Mapped[Optional[str]] = mapped_column(Text, Computed("lower(((given_names || ' '::text) || family_name))", persisted=True))

    users: Mapped['Users'] = relationship('Users', back_populates='patients')
    org: Mapped['Organisations'] = relationship('Organisations', back_populates='patients')
    ward: Mapped[Optional['Wards']] = relationship('Wards', back_populates='patients')
    tag: Mapped[List['Tags']] = relationship('Tags', secondary='patient_tags', back_populates='patient')
    abc_submissions: Mapped[List['AbcSubmissions']] = relationship('AbcSubmissions', back_populates='patient')
    abs_submissions: Mapped[List['AbsSubmissions']] = relationship('AbsSubmissions', back_populates='patient')
    care_tips: Mapped[List['CareTips']] = relationship('CareTips', back_populates='patient')
    care_tips_history: Mapped[List['CareTipsHistory']] = relationship('CareTipsHistory', back_populates='patient')
    key_events: Mapped[List['KeyEvents']] = relationship('KeyEvents', back_populates='patient')
    oasmnr_submissions: Mapped[List['OasmnrSubmissions']] = relationship('OasmnrSubmissions', back_populates='patient')
    patient_bookmarks: Mapped[List['PatientBookmarks']] = relationship('PatientBookmarks', back_populates='patient')
    patient_history: Mapped[List['PatientHistory']] = relationship('PatientHistory', back_populates='patient')


class AbcSubmissions(Base):
    __tablename__ = 'abc_submissions'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abc_submissions_created_by_fkey'),
        ForeignKeyConstraint(['last_updated_by'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', name='abc_submissions_last_updated_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abc_submissions_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='abc_submissions_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_by: Mapped[str] = mapped_column(Text)
    severity: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DELETED', name='AssessmentStatus'), server_default=text('\'ACTIVE\'::"AssessmentStatus"'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    additional_comments: Mapped[Optional[str]] = mapped_column(Text)
    actions_taken: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    before_events: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    behaviour: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    environment: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    perceived_feelings: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    location: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    people_present: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))
    last_updated_by: Mapped[Optional[str]] = mapped_column(Text)
    restraint_techniques: Mapped[Optional[list]] = mapped_column(ARRAY(Text()))

    users: Mapped['Users'] = relationship('Users', foreign_keys=[created_by], back_populates='abc_submissions')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[last_updated_by], back_populates='abc_submissions_')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='abc_submissions')
    abc_history: Mapped[List['AbcHistory']] = relationship('AbcHistory', back_populates='abc')


class AbsSubmissions(Base):
    __tablename__ = 'abs_submissions'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abs_submissions_created_by_fkey'),
        ForeignKeyConstraint(['last_updated_by'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', name='abs_submissions_last_updated_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abs_submissions_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='abs_submissions_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    anger: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    attention: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    emotion_trigger: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    impulsivity: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    fluctuating_mood: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    pulling_equipment: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    repetitive_behaviour: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    restlessness: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    self_abusiveness: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    self_stimulation: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    talking: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    uncooperative: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    violence: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    wandering: Mapped[int] = mapped_column(Integer, server_default=text('0'))
    observation_start: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    observation_end: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    observation_location: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DELETED', name='AssessmentStatus'), server_default=text('\'ACTIVE\'::"AssessmentStatus"'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    additional_comments: Mapped[Optional[str]] = mapped_column(Text)
    score: Mapped[Optional[int]] = mapped_column(Integer)
    severity: Mapped[Optional[str]] = mapped_column(Enum('NORMAL', 'MILD', 'MODERATE', 'SEVERE', name='SeverityLevels'))
    last_updated_by: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped['Users'] = relationship('Users', foreign_keys=[created_by], back_populates='abs_submissions')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[last_updated_by], back_populates='abs_submissions_')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='abs_submissions')
    abs_history: Mapped[List['AbsHistory']] = relationship('AbsHistory', back_populates='abs')


class CareTips(Base):
    __tablename__ = 'care_tips'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='care_tips_created_by_fkey'),
        ForeignKeyConstraint(['modified_by'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', name='care_tips_modified_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='care_tips_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='care_tips_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    created_by: Mapped[str] = mapped_column(Text)
    modified_by: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped['Users'] = relationship('Users', foreign_keys=[created_by], back_populates='care_tips')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[modified_by], back_populates='care_tips_')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='care_tips')
    user: Mapped[List['Users']] = relationship('Users', secondary='care_tip_likes', back_populates='care_tip')


class CareTipsHistory(Base):
    __tablename__ = 'care_tips_history'
    __table_args__ = (
        ForeignKeyConstraint(['modified_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='care_tips_history_modified_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='care_tips_history_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='care_tips_history_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    care_tip_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    modified_by: Mapped[str] = mapped_column(Text)
    modified_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    info: Mapped[Optional[dict]] = mapped_column(JSONB)

    users: Mapped['Users'] = relationship('Users', back_populates='care_tips_history')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='care_tips_history')


class KeyEvents(Base):
    __tablename__ = 'key_events'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='key_events_created_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='key_events_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='key_events_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    title: Mapped[str] = mapped_column(Text)
    start: Mapped[datetime.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DELETED', name='KeyEventStatus'), server_default=text('\'ACTIVE\'::"KeyEventStatus"'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped['Users'] = relationship('Users', back_populates='key_events')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='key_events')


class OasmnrSubmissions(Base):
    __tablename__ = 'oasmnr_submissions'
    __table_args__ = (
        CheckConstraint('antecedent >= 11 AND antecedent <= 25', name='check_antecedent'),
        CheckConstraint("intervention::text ~ '^[A-N]$'::text", name='check_intervention'),
        CheckConstraint('severity >= 1 AND severity <= 4', name='check_severity'),
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='oasmnr_submissions_created_by_fkey'),
        ForeignKeyConstraint(['last_updated_by'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', name='oasmnr_submissions_last_updated_by_fkey'),
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='oasmnr_submissions_patient_id_fkey'),
        PrimaryKeyConstraint('id', name='oasmnr_submissions_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    time_of_behaviour: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    behaviour: Mapped[str] = mapped_column(Enum('VA', 'PO', 'PS', 'PP', 'VC', 'NC', 'E', 'TO', name='OASMNRBehaviours'))
    severity: Mapped[int] = mapped_column(Integer)
    antecedent: Mapped[int] = mapped_column(Integer)
    intervention: Mapped[str] = mapped_column(String(1))
    recordings: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DELETED', name='AssessmentStatus'), server_default=text('\'ACTIVE\'::"AssessmentStatus"'))
    assessment_type: Mapped[str] = mapped_column(Text)
    contributing_factors: Mapped[Optional[list]] = mapped_column(ARRAY(Enum('StructuredActivity', 'NoisyEnvironment', 'RecentEpilepticFit', name='ContributingFactors', _create_events=False)))
    antecedent_other: Mapped[Optional[str]] = mapped_column(Text)
    intervention_other: Mapped[Optional[str]] = mapped_column(Text)
    severity_score: Mapped[Optional[int]] = mapped_column(Integer)
    intrusiveness: Mapped[Optional[int]] = mapped_column(Integer)
    last_updated_by: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped['Users'] = relationship('Users', foreign_keys=[created_by], back_populates='oasmnr_submissions')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[last_updated_by], back_populates='oasmnr_submissions_')
    patient: Mapped['Patients'] = relationship('Patients', back_populates='oasmnr_submissions')
    oasmnr_history: Mapped[List['OasmnrHistory']] = relationship('OasmnrHistory', back_populates='oasmnr')


class PatientBookmarks(Base):
    __tablename__ = 'patient_bookmarks'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patient_bookmarks_patient_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patient_bookmarks_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'patient_id', name='patient_bookmarks_pkey')
    )

    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))

    patient: Mapped['Patients'] = relationship('Patients', back_populates='patient_bookmarks')
    user: Mapped['Users'] = relationship('Users', back_populates='patient_bookmarks')


class PatientHistory(Base):
    __tablename__ = 'patient_history'
    __table_args__ = (
        ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patient_history_patient_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patient_history_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='patient_history_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DISCHARGED', 'DELETED', name='PatientStatus'))
    updated_by: Mapped[str] = mapped_column(Text)
    update_info: Mapped[Optional[dict]] = mapped_column(JSONB)

    patient: Mapped['Patients'] = relationship('Patients', back_populates='patient_history')
    users: Mapped['Users'] = relationship('Users', back_populates='patient_history')


t_patient_tags = Table(
    'patient_tags', Base.metadata,
    Column('patient_id', Uuid, primary_key=True, nullable=False),
    Column('tag_id', Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT', onupdate='CASCADE', name='patient_tags_patient_id_fkey'),
    ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE', onupdate='CASCADE', name='patient_tags_tag_id_fkey'),
    PrimaryKeyConstraint('patient_id', 'tag_id', name='patient_tags_pkey')
)


class AbcHistory(Base):
    __tablename__ = 'abc_history'
    __table_args__ = (
        ForeignKeyConstraint(['abc_id'], ['abc_submissions.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abc_history_abc_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abc_history_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='abc_history_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    abc_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    updated_by: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[str] = mapped_column(Text)
    update_info: Mapped[Optional[dict]] = mapped_column(JSONB)

    abc: Mapped['AbcSubmissions'] = relationship('AbcSubmissions', back_populates='abc_history')
    users: Mapped['Users'] = relationship('Users', back_populates='abc_history')


class AbsHistory(Base):
    __tablename__ = 'abs_history'
    __table_args__ = (
        ForeignKeyConstraint(['abs_id'], ['abs_submissions.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abs_history_abs_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='abs_history_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='abs_history_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    abs_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    updated_by: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[str] = mapped_column(Text)
    update_info: Mapped[Optional[dict]] = mapped_column(JSONB)

    abs: Mapped['AbsSubmissions'] = relationship('AbsSubmissions', back_populates='abs_history')
    users: Mapped['Users'] = relationship('Users', back_populates='abs_history')


t_care_tip_likes = Table(
    'care_tip_likes', Base.metadata,
    Column('care_tip_id', Uuid, primary_key=True, nullable=False),
    Column('user_id', Text, primary_key=True, nullable=False),
    ForeignKeyConstraint(['care_tip_id'], ['care_tips.id'], ondelete='CASCADE', onupdate='CASCADE', name='care_tip_likes_care_tip_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='care_tip_likes_user_id_fkey'),
    PrimaryKeyConstraint('care_tip_id', 'user_id', name='care_tip_likes_pkey')
)


class OasmnrHistory(Base):
    __tablename__ = 'oasmnr_history'
    __table_args__ = (
        ForeignKeyConstraint(['oasmnr_id'], ['oasmnr_submissions.id'], ondelete='RESTRICT', onupdate='CASCADE', name='oasmnr_history_oasmnr_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', name='oasmnr_history_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='oasmnr_history_pkey')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    oasmnr_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    updated_by: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3))
    status: Mapped[str] = mapped_column(Enum('ACTIVE', 'DELETED', name='AssessmentStatus'))
    update_info: Mapped[Optional[dict]] = mapped_column(JSONB)

    oasmnr: Mapped['OasmnrSubmissions'] = relationship('OasmnrSubmissions', back_populates='oasmnr_history')
    users: Mapped['Users'] = relationship('Users', back_populates='oasmnr_history')
