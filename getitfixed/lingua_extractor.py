from lingua.extractors import Extractor, Message
from c2c.template.config import config as configuration


class GetItFixedExtractor(Extractor):  # pragma: no cover
    """
    GetItFixed extractor (settings: emails subjects and bodys)
    """

    extensions = [".yaml"]

    def __call__(self, filename, options):
        configuration.init(filename)
        settings = configuration.get_config()

        for path in (
            ("getitfixed", "admin_new_issue_email", "email_subject"),
            ("getitfixed", "admin_new_issue_email", "email_body"),
            ("getitfixed", "new_issue_email", "email_subject"),
            ("getitfixed", "new_issue_email", "email_body"),
            ("getitfixed", "update_issue_email", "email_subject"),
            ("getitfixed", "update_issue_email", "email_body"),
            ("getitfixed", "resolved_issue_email", "email_subject"),
            ("getitfixed", "resolved_issue_email", "email_body"),
        ):
            value = settings
            for key in path:
                value = value[key]
            # yield Message(msgctxt msgid msgid_plural flags comment tcomment location)
            yield Message(None, value, None, [], u"", u"", (filename, "/".join(path)))
