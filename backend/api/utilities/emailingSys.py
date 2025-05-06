from email.message import EmailMessage
import os
import mimetypes
import smtplib

def message_creator(sender: str, recipients: list, subject:str, body: str, attachment_path:str):
    """_summary_

    Args:
        sender (str): _description_
        recipients (list): _description_
        subject (str): _description_
        body (str): _description_
        attachment_path (str): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    if sender and recipients and subject and body:
        message = EmailMessage()
        message['From'] = sender
        message['To'] = ";".join(recipients)
        message['Subject'] = subject
        message.set_content(body)

        if attachment_path:
            filename, mime_type, mime_subtype = mime_setup(attachment_path=attachment_path)

            with open(attachment_path, 'rb') as attached:
                message.add_attachment(attached.read(),
                                    maintype = mime_type,
                                    subtype = mime_subtype,
                                    filename = filename)

        return message
    raise ValueError('You must include a sender, recipients, subject, and body.')


def mime_setup(attachment_path:str):
    """Used to return the base file name, mime_type, and mime_sub type to properly 
    attach documents to emails.

    Args:
        attachment_path (str): Path to file held in tmp storage.

    Returns:
        filename (str): _description_
        mime_type (str): _description_
        mime_subtype (str): _description_
    """
    filename = os.path.basename(attachment_path)

    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split('/', 1)

    return filename, mime_type, mime_subtype

def send_mail(message: EmailMessage,
              smptp_user: str, smtp_pass:str):
    """
    Connect to Office365 SMTP, authenticate, and send the prepared EmailMessage.

    Args:
        message (EmailMessage): Message created from messageCreater() function.
        smptp_user (str): User to authenticate with.
        smtp_pass (str): User's passwords stored in environmental variable.
    """
    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smptp_user, smtp_pass)
        smtp.send_message(message)
