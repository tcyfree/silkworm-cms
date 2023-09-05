from applications.extensions import ma
from marshmallow import fields


class PhotoOutSchema(ma.Schema):
    id = fields.Integer()
    name = fields.Str()
    href = fields.Str()
    mime = fields.Str()
    address = fields.Str()
    remark = fields.Str()
    reply = fields.Str()
    size = fields.Str()
    ext = fields.Str()
    username = fields.Str()
    reply_username = fields.Str()
    create_time = fields.DateTime()
