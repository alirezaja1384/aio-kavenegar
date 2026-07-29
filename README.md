# aio-kavenegar

# <a href="http://kavenegar.com/rest.html">Kavenegar RESTful API Document</a>
If you need to future information about API document Please visit RESTful Document

## Caution !
**This repository IS NOT AN OFFICIAL KAVENEGAR CLIENT!**

**This project is not compatible with the official package.**

The original repository can be found [Here](https://github.com/kavenegarkavenegar-python/).


## Installation
<p> You can install our SDK from pypi through below command </p>


```
pip install aio-kavenegar
```
You can download the Python SDK <a href="https://github.com/alirezaja1384/aio-kavenegar/blob/main/kavenegar.py">Here</a> too
<p>
Then ,You need to make an account on Kavenegar from <a href="https://panel.kavenegar.com/Client/Membership/Register">Here</a>
</p>
<p>
After that you just need to pick API-KEY up from <a href="http://panel.kavenegar.com/Client/setting/index">My Account</a> section.

Anyway there is good tutorial about <a href="http://gun.io/blog/how-to-github-fork-branch-and-pull-request/">Pull  request</a>
</p>

## Usage

Well, There is an example to Send SMS by Python below. `timeout` parameter is optional in `AIOKavenegarAPI` constructor, default value is set to 10 seconds.

### Send
```python
#!/usr/bin/env python
import asyncio
from aio_kavenegar import AIOKavenegarAPI, APIException, HTTPException


async def main():
    try:
        api = AIOKavenegarAPI('Your APIKey', timeout=20)
        params = {
            'sender': '',#optional
            'receptor': '',#multiple mobile number, split by comma
            'message': '',
        } 
        response = await api.sms_send(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
```
### OTP
```python
#!/usr/bin/env python
import asyncio
from aio_kavenegar import AIOKavenegarAPI, APIException, HTTPException


async def main():
    try:
        api = AIOKavenegarAPI('Your APIKey', timeout=20)
        params = {
            'receptor': '',
            'template': '',
            'token': '',
            'type': 'sms',#sms vs call
        }   
        response = await api.verify_lookup(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
```
### Send Bulk
```python
#!/usr/bin/env python
import asyncio
from aio_kavenegar import AIOKavenegarAPI, APIException, HTTPException


async def main():
    try:
        api = AIOKavenegarAPI('Your APIKey', timeout=20)
        params = {
            'sender':'["",""]',#array of string as json 
            'receptor': '["",""]',#array of string as json 
            'message': '["",""]',#array of string as json 
        } 
        response = await api.sms_sendarray(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
```

# Contribution
Bug fixes, docs, and enhancements welcome! Please let us know <a href="mailto:support@kavenegar.com?Subject=SDK" target="_top">support@kavenegar.com</a>
<hr>
<div dir='rtl'>

## توجه !
**این یک نسخه رسمی کلاینت کاوه نگار نیست!**

**این پروژه با پکیج رسمی کاوه نگار سازگار نیست.**

کلاینت رسمی را می توانید در [اینجا](https://github.com/kavenegar/kavenegar-python/) مشاهده کنید.


## راهنما

### معرفی سرویس کاوه نگار

کاوه نگار یک وب سرویس ارسال و دریافت پیامک و تماس صوتی است که به راحتی میتوانید از آن استفاده نمایید.

### ساخت حساب کاربری

اگر در وب سرویس کاوه نگار عضو نیستید میتوانید از [لینک عضویت](http://panel.kavenegar.com/client/membership/register) ثبت نام  و اکانت آزمایشی برای تست API دریافت نمایید.

### مستندات

برای مشاهده اطلاعات کامل مستندات [وب سرویس پیامک](http://kavenegar.com/وب-سرویس-پیامک.html)  به صفحه [مستندات وب سرویس](http://kavenegar.com/rest.html) مراجعه نمایید.

### راهنمای فارسی

در صورتی که مایل هستید راهنمای فارسی کیت توسعه کاوه نگار را مطالعه کنید به صفحه [کد ارسال پیامک](http://kavenegar.com/sdk.html) مراجعه نمایید.

### اطالاعات بیشتر
برای مطالعه بیشتر به صفحه معرفی
[وب سرویس اس ام اس ](http://kavenegar.com)
کاوه نگار
مراجعه نمایید .

 اگر در استفاده از کیت های سرویس کاوه نگار مشکلی یا پیشنهادی  داشتید ما را با یک Pull Request  یا  ارسال ایمیل به support@kavenegar.com  خوشحال کنید.
 
##
![http://kavenegar.com](http://kavenegar.com/public/images/logo.png)		

[http://kavenegar.com](http://kavenegar.com)	

</div>



