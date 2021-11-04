import logging
import os
import secrets
import uuid
from datetime import datetime

import werkzeug
from flask import Flask
from flask_login import AnonymousUserMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

from modep_common import settings
from modep_common.io import StorageClient


logger = logging.getLogger(__name__)

db = SQLAlchemy()


def get_app_and_db():
    app = Flask("app")
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CELERY_BROKER_URL"] = os.environ.get("CELERY_BROKER_URL", None)
    app.config["CELERY_RESULT_BACKEND"] = os.environ.get("CELERY_RESULT_BACKEND", None)
    db = SQLAlchemy(app)
    return app, db


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class StatusMixin(object):
    status = db.Column(db.String(16), nullable=True)
    info = db.Column(db.String(512), default="")
    job_name = db.Column(db.String(128), default="")


class AnonUser(AnonymousUserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(256), unique=True)
    nb_requests = db.Column(db.Integer)

    def __init__(self):
        self.nb_requests = 0

    def __repr__(self):
        return "<AnonUser id=%r, ip=%r, nb_requests = %i>" % (
            self.id,
            self.ip,
            self.nb_requests,
        )


class User(UserMixin, TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    pwd_hash = db.Column(db.String(512))
    nb_requests = db.Column(db.Integer)
    ip = db.Column(db.String(256))
    api_key = db.Column(db.String(128))
    tier = db.Column(db.String(16))
    tier_info = db.Column(db.String(512))

    def __init__(self, email, password, ip, tier="free"):
        self.id = str(uuid.uuid4())
        self.email = email
        self.set_password(password)
        self.ip = ip
        self.nb_requests = 0
        self.tier = tier
        self.api_key = secrets.token_urlsafe(16)

    def set_password(self, password):
        self.pwd_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password):
        return werkzeug.security.check_password_hash(self.pwd_hash, password)

    def __repr__(self):
        return "<User email=%r>" % (self.email)


class ContactForm(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    user_is_anon = db.Column(db.Boolean)
    user_email = db.Column(db.String(128), unique=False)
    msg = db.Column(db.Text)


class TabularDataset(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    path = db.Column(db.String(512))
    gcp_path = db.Column(db.String(512))
    name = db.Column(db.String(128))
    ext = db.Column(db.String(10))
    mbytes = db.Column(db.Float)
    columns = db.Column(db.JSON)
    is_public = db.Column(db.Boolean, default=False)

    def __init__(self, id, user_pk, path, gcp_path, name, ext, mbytes, columns=[]):
        self.id = id
        self.user_pk = user_pk
        self.path = path
        self.gcp_path = gcp_path
        self.name = name
        self.ext = ext
        self.mbytes = mbytes
        self.columns = columns


class TabularFramework(TimestampMixin, StatusMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), unique=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)

    # framework service identifiers
    framework_pk = db.Column(
        db.Integer, db.ForeignKey("tabular_framework_service.pk"), nullable=True
    )
    framework_id = db.Column(db.String(32), nullable=True)
    framework_name = db.Column(db.String(32), nullable=True)

    # Flight class also has these next ones
    train_ids = db.Column(db.JSON)
    test_ids = db.Column(db.JSON)
    target = db.Column(db.String(32))
    max_runtime_seconds = db.Column(db.Integer)

    is_class = db.Column(db.Boolean)
    gcp_path = db.Column(db.String(512), nullable=True)
    gcp_model_paths = db.Column(db.JSON)

    fold_meta = db.Column(db.JSON)
    fold_results = db.Column(db.JSON)
    fold_leaderboard = db.Column(db.JSON)
    fold_model_txt = db.Column(db.JSON)
    n_folds = db.Column(db.Integer)

    outdir = db.Column(db.String(512), nullable=True)
    version = db.Column(db.String(16), nullable=True)
    metric_name = db.Column(db.String(16), nullable=True)
    metric_value = db.Column(db.Float)
    other_metrics = db.Column(db.JSON)
    problem_type = db.Column(db.String(16))

    duration = db.Column(db.Float)
    training_duration = db.Column(db.Float)
    predict_duration = db.Column(db.Float)

    models_count = db.Column(db.Integer)
    experiment_id = db.Column(db.String(64))
    task_id = db.Column(db.String(64), unique=True)

    flight_pk = db.Column(
        db.Integer,
        db.ForeignKey("tabular_framework_flight.pk", ondelete="CASCADE"),
        nullable=True,
    )

    def __init__(
        self,
        user_pk=None,
        framework_id=None,
        framework_pk=None,
        framework_name=None,
        train_ids=None,
        test_ids=None,
        target=None,
        is_class=None,
        max_runtime_seconds=None,
        predictions=None,
        meta=None,
        results=None,
        n_folds=None,
        leaderboard=None,
        task_id=None,
        outdir=None,
        experiment_id=None,
    ):

        self.id = str(uuid.uuid4())
        self.user_pk = user_pk
        self.framework_id = framework_id
        self.framework_pk = framework_pk
        self.framework_name = framework_name
        self.train_ids = train_ids
        self.test_ids = test_ids
        self.target = target
        self.is_class = is_class
        self.max_runtime_seconds = max_runtime_seconds
        self.predictions = predictions
        self.meta = meta
        self.results = results
        self.n_folds = n_folds
        self.leaderboard = leaderboard
        self.task_id = task_id
        self.outdir = outdir
        self.experiment_id = experiment_id

    def delete_remote(self):
        sc = StorageClient()

        # delete outdir zip
        sc.try_to_delete(self.gcp_path)

        # delete models
        if self.gcp_model_paths is not None:
            for gcp_path in self.gcp_model_paths:
                sc.try_to_delete(gcp_path)

        # delete predictions
        preds = TabularFrameworkPredictions.query.filter_by(framework_pk=self.pk)
        for pred in preds:
            sc.try_to_delete(pred.gcp_path)

        # delete job yaml
        sc.try_to_delete(f"tabular-frameworks/{self.id}/job.yaml")


class TabularFrameworkPredictions(TimestampMixin, StatusMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), unique=True)
    user_pk = db.Column(
        db.Integer, db.ForeignKey("user.pk", ondelete="CASCADE"), nullable=True
    )
    framework_pk = db.Column(
        db.Integer,
        db.ForeignKey("tabular_framework.pk", ondelete="CASCADE"),
        nullable=True,
    )
    dataset_pk = db.Column(
        db.Integer,
        db.ForeignKey("tabular_dataset.pk", ondelete="CASCADE"),
        nullable=True,
    )
    fold = db.Column(db.Integer)
    path = db.Column(db.String(512))
    gcp_path = db.Column(db.String(512), nullable=True)

    def __init__(
        self, user_pk, framework_pk, dataset_pk, fold, path=None, gcp_path=None
    ):
        self.id = str(uuid.uuid4())
        self.user_pk = user_pk
        self.framework_pk = framework_pk
        self.dataset_pk = dataset_pk
        self.fold = fold
        if path is not None:
            self.path = path
        if gcp_path is not None:
            self.gcp_path = None


class TabularFrameworkService(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    framework_name = db.Column(db.String(32), nullable=True, unique=True)
    framework_id = db.Column(db.String(32), nullable=True, unique=True)
    service_id = db.Column(db.String(32), nullable=True)
    version = db.Column(db.String(16), nullable=True)
    description = db.Column(db.String(512), nullable=True)
    project = db.Column(db.String(256), nullable=True)
    refs = db.Column(db.JSON)
    params = db.Column(db.JSON)
    extends = db.Column(db.String(128))
    has_predict = db.Column(db.Boolean, default=True)
    image_name = db.Column(db.String(32), nullable=True)

    def __init__(
        self,
        framework_name=None,
        framework_id=None,
        service_id=None,
        description=None,
        project=None,
        refs=None,
        params=None,
        extends=None,
        has_predict=True,
        version=None,
        image_name=None,
    ):
        self.id = str(uuid.uuid4())
        self.framework_name = framework_name
        self.framework_id = framework_id
        self.service_id = service_id
        self.description = description
        self.project = project
        self.refs = refs
        self.params = params
        self.extends = extends
        self.has_predict = has_predict
        self.version = version
        self.image_name = image_name


class TabularFrameworkFlight(TimestampMixin, StatusMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    frameworks = db.relationship(
        "TabularFramework",
        backref="tabular_framework_flight",
        lazy=True,
        order_by="TabularFramework.pk",
    )
    framework_names = db.Column(db.JSON)

    train_ids = db.Column(db.JSON)
    test_ids = db.Column(db.JSON)
    target = db.Column(db.String(32))
    max_runtime_seconds = db.Column(db.Integer)

    def __init__(
        self, user_pk, framework_names, train_ids, test_ids, target, max_runtime_seconds
    ):
        self.id = str(uuid.uuid4())
        self.user_pk = user_pk
        self.framework_names = framework_names
        self.train_ids = train_ids
        self.test_ids = test_ids
        self.target = target
        self.max_runtime_seconds = max_runtime_seconds


class DeploymentWriteup(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    name = db.Column(db.String(64))
    content = db.Column(db.Text)

    def __init__(self, name=None, content=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.content = content


class StripeCustomer(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    subscription_id = db.Column(db.String(255), nullable=True)


class StripeCheckoutSession(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    subscription_id = db.Column(db.String(255), nullable=True)
    checkout_session = db.Column(db.JSON)


class StripeInvoice(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    invoice = db.Column(db.JSON)


class ApiTier(TimestampMixin, db.Model):
    """Default set of tiers, excluding custom tier"""

    id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(16), unique=True)
    concurrency = db.Column(db.Integer)
    max_cpus = db.Column(db.Integer)
    max_gpus = db.Column(db.Integer)
    max_runtime_seconds = db.Column(db.Integer)

    def __init__(self, tier_name, concurrency, max_cpus, max_gpus, max_runtime_seconds):
        self.tier_name = tier_name
        self.concurrency = concurrency
        self.max_cpus = max_cpus
        self.max_gpus = max_gpus
        self.max_runtime_seconds = max_runtime_seconds

    @staticmethod
    def create_all():
        TIERS = {
            "free": {
                "concurrency": 1,
                "max_cpus": 8,
                "max_gpus": 0,
                "max_runtime_seconds": int(60 * 10),
            },
            "supporter": {
                "concurrency": 1,
                "max_cpus": 8,
                "max_gpus": 0,
                "max_runtime_seconds": int(60 * 30),
            },
            "lab": {
                "concurrency": 2,
                "max_cpus": 16,
                "max_gpus": 0,
                "max_runtime_seconds": int(60 * 60),
            },
            "startup": {
                "concurrency": 4,
                "max_cpus": 32,
                "max_gpus": 0,
                "max_runtime_seconds": int(60 * 60 * 8),
            },
        }
        for tier_name, tier_kwargs in TIERS.items():
            tier = ApiTier.query.filter_by(tier_name=tier_name)
            if tier.count() == 0:
                tier_kwargs["tier_name"] = tier_name
                tier = ApiTier(**tier_kwargs)
            else:
                tier.update(tier_kwargs)
                tier = tier[0]
            db.session.add(tier)
            db.session.commit()


class UserQuota(TimestampMixin, db.Model):
    """Can be set customized per user"""

    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey("user.pk"), nullable=True)
    concurrency = db.Column(db.Integer)
    max_cpus = db.Column(db.Integer)
    max_gpus = db.Column(db.Integer)
    max_runtime_seconds = db.Column(db.Integer)

    def __init__(self, user):
        self.user_pk = user.pk
        self.set_from_tier(user.tier)

    def set_from_tier(self, tier_name):
        if tier_name == "custom":
            logger.info('Not using preset quotas for tier: "%s"', tier_name)
            return

        tier = ApiTier.query.filter_by(tier_name=tier_name).one()

        self.concurrency = tier.concurrency
        self.max_cpus = tier.max_cpus
        self.max_gpus = tier.max_gpus
        self.max_runtime_seconds = tier.max_runtime_seconds


def test_db():
    app, db = get_app_and_db()
    with app.app_context():
        users = User.query.all()
        print(users)


if __name__ == '__main__':
    test_db()
