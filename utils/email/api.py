import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class EmailSender:
    def __init__(self, smtp_server, port, sender_email, sender_password):
        """
            初始化
        :param smtp_server: SMTP服务器地址，用于指定邮件发送的服务器
        :param port: SMTP服务器端口，用于建立连接的特定端口号
        :param sender_email: 发件人的邮箱地址，用于身份验证和邮件发送
        :param sender_password: 发件人的邮箱密码，用于身份验证
        """
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.server = None

    def connect(self):
        """
            连接SMTP服务器
        :return:
        """
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.port)
        self.server.login(self.sender_email, self.sender_password)

    def disconnect(self):
        """
            断开SMTP服务器连接
        :return:
        """
        if self.server is not None:
            self.server.quit()

    def send_text_email(self, receiver_emails, subject, body, cc_emails=None):
        """
            发送纯文本邮件给一个或多个收件人
        :param receiver_emails: 收件人的电子邮件地址列表
        :param subject: 邮件主题
        :param body: 邮件正文内容
        :param cc_emails: 抄送的电子邮件地址列表，默认为None
        :return: 无
        """
        # 创建一个多部分的邮件消息对象
        msg = MIMEMultipart()
        # 设置邮件的发件人
        msg['From'] = self.sender_email
        # 设置邮件的收件人（多个收件人以逗号分隔）
        msg['To'] = ', '.join(receiver_emails)
        # 设置邮件的主题
        msg['Subject'] = subject
        # 将邮件正文添加为纯文本格式到邮件消息对象中
        msg.attach(MIMEText(body, 'plain'))

        # 如果提供了抄送列表，则添加抄送信息到邮件中
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)

        # 连接到邮件服务器
        self.connect()
        # 发送邮件，将收件人列表和抄送列表合并为邮件接收者列表
        self.server.sendmail(self.sender_email, receiver_emails + (cc_emails or []), msg.as_string())
        # 断开与邮件服务器的连接
        self.disconnect()

    def send_attachment_email(self, receiver_emails, subject, body, file_path, filename=None, cc_emails=None):
        """
            发送带有附件的邮件
        :param receiver_emails:  收件人的电子邮件地址列表
        :param subject: 主题
        :param body:  文件正文
        :param file_path: 文件路径
        :param filename: 文件名
        :param cc_emails: 抄送的电子邮件地址列表，默认为None
        :return:
        """
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(receiver_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # 添加附件
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=(filename or file_path.split('/')[-1]))
        part['Content-Disposition'] = f'attachment; filename="{part.get_filename()}"'
        msg.attach(part)

        # 添加抄送
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)

        self.connect()
        self.server.sendmail(self.sender_email, receiver_emails + (cc_emails or []), msg.as_string())
        self.disconnect()


# 使用示例
if __name__ == "__main__":
    email_sender = EmailSender(smtp_server='smtp.qq.com',
                               port=465,
                               sender_email='@qq.com',
                               sender_password='tpioiyfkudczbija')

    email_sender.send_text_email(receiver_emails=['chuanqidota@126.com'],
                                 subject='Test Email',
                                 body='This is a test email.',
                                 cc_emails=['chuanqidota@126.com'])

    email_sender.send_attachment_email(receiver_emails=['chuanqidota@126.com'],
                                       subject='Email with Attachment',
                                       body='Please find the attached file.',
                                       file_path='/tmp/a.txt',
                                       cc_emails=['chuanqidota@126.com'])
