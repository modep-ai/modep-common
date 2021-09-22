import uuid
import secrets
from datetime import datetime
import werkzeug

from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin, UserMixin


db = SQLAlchemy()


class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class AnonUser(AnonymousUserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(256), unique=True)
    nb_requests = db.Column(db.Integer)

    def __init__(self):
        self.nb_requests = 0

    def __repr__(self):
        return '<AnonUser id=%r, ip=%r, nb_requests = %i>' % (self.id, self.ip, self.nb_requests)


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

    def __init__(self, email, password, ip, tier='free'):
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
        return '<User email=%r>' % (self.email)


class StripeCustomer(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    subscription_id = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return '<StripeCustomer id=%r, user_pk=%r, customer_id=%r, subscription_id=%r, created=%r>' % \
                (self.id, self.user_pk, self.customer_id, self.subscription_id, self.created)


class StripeCheckoutSession(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    subscription_id = db.Column(db.String(255), nullable=True)
    checkout_session = db.Column(db.JSON)


class StripeInvoice(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)
    customer_id = db.Column(db.String(255), nullable=True)
    invoice = db.Column(db.JSON)


class ContactForm(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)
    user_is_anon = db.Column(db.Boolean)
    user_email = db.Column(db.String(128), unique=False)
    msg = db.Column(db.Text)


class TabularDataset(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)
    path = db.Column(db.String(512))
    gcp_path = db.Column(db.String(512))
    name = db.Column(db.String(128))
    ext = db.Column(db.String(10))
    mbytes = db.Column(db.Float)

    def __init__(self, id, user_pk, path, gcp_path, name, ext, mbytes):
        self.id = id
        self.user_pk = user_pk
        self.path = path
        self.gcp_path = gcp_path
        self.name = name
        self.ext = ext
        self.mbytes = mbytes


class TabularFramework(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), unique=True)
    user_pk = db.Column(db.Integer, db.ForeignKey('user.pk'), nullable=True)

    framework_id = db.Column(db.String(32), nullable=True)
    framework_pk = db.Column(db.Integer, db.ForeignKey('tabular_framework_service.pk'), nullable=True)
    framework_name = db.Column(db.String(32), nullable=True)

    train_ids = db.Column(db.JSON)
    test_ids =  db.Column(db.JSON)
    target = db.Column(db.String(32))
    is_class = db.Column(db.Boolean)
    max_runtime_seconds = db.Column(db.Integer)
    gcp_path = db.Column(db.String(512), nullable=True)
    gcp_model_paths = db.Column(db.JSON)
    status = db.Column(db.String(16), nullable=True)

    fold_meta = db.Column(db.JSON)
    fold_results = db.Column(db.JSON)
    fold_leaderboard = db.Column(db.JSON)
    fold_model_txt = db.Column(db.JSON)
    n_folds = db.Column(db.Integer)

    task_id = db.Column(db.String(64), unique=True)
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
    info = db.Column(db.String(256))
    experiment_id = db.Column(db.String(64))

    def __init__(self, user_pk=None, framework_id=None, framework_pk=None, framework_name=None,
                 train_ids=None, test_ids=None, target=None,
                 is_class=None, max_runtime_seconds=None,
                 predictions=None, meta=None, results=None, n_folds=None, leaderboard=None,
                 task_id=None, outdir=None, experiment_id=None):

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


class TabularFrameworkPredictions(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), unique=True)
    framework_pk = db.Column(db.Integer, db.ForeignKey('tabular_framework.pk', ondelete='CASCADE'), nullable=True)
    dataset_pk = db.Column(db.Integer, db.ForeignKey('tabular_dataset.pk', ondelete='CASCADE'), nullable=True)
    fold = db.Column(db.Integer)
    path = db.Column(db.String(512))
    gcp_path = db.Column(db.String(512), nullable=True)
    status = db.Column(db.String(16), nullable=True)

    def __init__(self, framework_pk, dataset_pk, fold, path=None, gcp_path=None):
        self.id = str(uuid.uuid4())
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
    description = db.Column(db.String(512), nullable=True)
    project = db.Column(db.String(256), nullable=True)
    refs = db.Column(db.JSON)
    params = db.Column(db.JSON)
    extends = db.Column(db.String(128))

    def __init__(self, framework_name=None, framework_id=None, service_id=None,
                 description=None, project=None, refs=None, params=None, extends=None):
        self.id = str(uuid.uuid4())
        self.framework_name = framework_name
        self.framework_id = framework_id
        self.service_id = service_id
        self.description = description
        self.project = project
        self.refs = refs
        self.params = params
        self.extends = extends


class DeploymentWriteup(TimestampMixin, db.Model):
    pk = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    name = db.Column(db.String(64))
    content = db.Column(db.Text)

    def __init__(self, name=None, content=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.content = content


if __name__ == '__main__':
    import fire
    fire.Fire()
