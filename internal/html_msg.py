def make_url(prefix_url, uid, checker):
    msg_link = "%s/user/email_confirm?email=%s&checker=%s" % (
        prefix_url,
        uid,
        checker,
    )
    return msg_link


def auth_msg(msg_link):
    auth_body = f"""
    <html>
    <head>
    </head>
    <body>
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center" style="background-color: #f2f2f2; padding: 20px;">
                    <h1 style="font-size: 64px; color: #333;">CYRUS 이메일 인증</h1>
                    <p style="font-size: 24px; margin-top: 20px; color: #555;">
                        이메일 인증을 완료하고 CYRUS를 사용하려면 아래 버튼을 클릭해주세요.
                    </p>
                    <a href='{msg_link}' style="text-decoration: none; background-color: #007bff; color: #fff; padding: 10px 20px; font-size: 20px; border-radius: 5px; margin-top: 20px; display: inline-block;">이메일 인증하기</a>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return auth_body


def html_ok_msg(web_url):
    html_ok_content = f"""
    <html>
    <head>
    </head>
    <body>
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center" style="background-color: #f2f2f2; padding: 20px;">
                    <h1 style="font-size: 64px; color: #333;">Certified</h1>
                    <h2 style="font-size: 24px; margin-top: 20px; color: #555;">이메일이 인증 되었습니다.</h2>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_ok_content


def html_ng_msg(web_url):
    html_ng_content = f"""
    <html>
    <head>
    </head>
    <body>
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td align="center" style="background-color: #f2f2f2; padding: 20px;">
                    <h1 style="font-size: 64px; color: #333;">certification failed</h1>
                    <h2 style="font-size: 24px; margin-top: 20px; color: #555;">이메일이 인증 되지 않았습니다.</h2>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html_ng_content
