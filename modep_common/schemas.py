from marshmallow import Schema, fields


class DefaultResponse(Schema):
    message = fields.String(default='Success')


class TabularFrameworkInfoSchema(Schema):
    class Meta:
        fields = ('framework_name', 'description', 'project', 'params')
        ordered = True


class TabularFrameworkParamsSchema(Schema):
    framework_name = fields.String(required=True, description="Name of the framework to train")
    train_ids = fields.List(fields.String(), required=True, description='IDs of datasets to train on')
    test_ids = fields.List(fields.String(), required=True, description='IDs of datasets to test on')
    target = fields.String(required=True, description='Target column to predict')
    max_runtime_seconds = fields.Int(required=True, description='Time in seconds to run')
    experiment_id = fields.String(required=False, description='Experiment tag for grouping runs', default='')


class TabularFrameworkSchema(Schema):
    class Meta:
        fields = (
            'id', 'framework_name', 'version', 'train_ids', 'test_ids', 'target', 'max_runtime_seconds',
            'created', 'status', 'problem_type', 'metric_name', 'metric_value', 'other_metrics',
            'duration', 'training_duration', 'predict_duration', 'models_count', 'n_folds',
            'fold_results', 'fold_leaderboard', 'fold_model_txt',
            'experiment_id', 'info',
        )
        ordered = True


class TabularFrameworkPredictSchema(Schema):
    framework_id = fields.String(required=True, description="ID of the trained framework")
    dataset_id = fields.String(required=True, description='ID of dataset to predict on')


class TabularFrameworkPredictionsSchema(Schema):
    class Meta:
        fields = ('id', 'framework_id', 'dataset_id', 'status', 'predictions')
        ordered = True
