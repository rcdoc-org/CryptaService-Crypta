from email.message import EmailMessage
import os
import mimetypes

def messageCreator(sender: str, recipients: list, subject:str, body: str, attachment_path:str):
    if sender and recipients and subject and body:
        message = EmailMessage()
        message['From'] = sender
        message['To'] = ";".join(recipients)
        message['Subject'] = subject
        message.set_content(body)

        if attachment_path:
            filename, mime_type, mime_subtype = mimeSetup(attachment_path=attachment_path)

            with open(attachment_path, 'rb') as attached:
                message.add_attachment(attached.read(),
                                    maintype = mime_type,
                                    subtype = mime_subtype,
                                    filename = filename)

        return message
    raise ValueError('You must include a sender, recipients, subject, and body.')


def mimeSetup(attachment_path:str):
    filename = os.path.basename(attachment_path)

    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split('/', 1)

    return filename, mime_type, mime_subtype
