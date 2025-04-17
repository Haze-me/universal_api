# Universal Sign-up API

A dynamic, universal API for handling sign-ups from any website with custom form fields, database connections, and email/SMS configurations.

## Features

1. **Company Registration System**
   - Store and manage company credentials, database info, and their target table

2. **Universal API Endpoint**
   - One single POST endpoint (`/api/submit`) that accepts dynamic form data
   - Connects to the company's DB using their credentials
   - Dynamically inserts the form data into the right table

3. **Support for Any Form Structure**
   - Flexible schema that adapts to any form fields

4. **Multiple Database Support**
   - MongoDB, PostgreSQL, MySQL, SQLite
   - Connect via parameters or connection string

5. **Customizable Email System**
   - Configure SMTP settings per company
   - Support for API-based email services (SendGrid, Mailgun, Postmark, Amazon SES)
   - Custom email templates for welcome, verification, and password reset
   - Default templates if not provided

6. **Customizable SMS System**
   - Custom SMS templates for welcome, verification, and password reset
   - Configure SMS provider settings per company (Twilio, Nexmo/Vonage, AWS SNS)
   - Default templates if not provided

7. **Verification Methods**
   - Email verification with 6-digit alphanumeric codes
   - Phone verification with SMS
   - Companies can choose their preferred verification method

8. **Custom Validation Rules**
   - Each company can define validation rules for their form fields

9. **Password Reset**
   - Password reset via email or SMS (using the company's preferred verification method)
   - Secure verification code system
   - Password hashing for security

## Setup

1. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

2. Create a `.env` file based on the provided `.env.sample`:
   \`\`\`
   cp .env.sample .env
   \`\`\`

3. Edit the `.env` file with your configuration

4. Run migrations:
   \`\`\`
   python manage.py migrate
   \`\`\`

5. Create a superuser:
   \`\`\`
   python manage.py createsuperuser
   \`\`\`

6. Run the server:
   \`\`\`
   python manage.py runserver
   \`\`\`

## API Usage

### Headers

All API requests require the following headers:
- `X-Company-ID`: The UUID of the company
- `X-API-Key`: The API key for the company (for authenticated endpoints)

### Endpoints

#### 1. Submit Form Data

\`\`\`
POST /api/submit/
\`\`\`

Request body: The form data to be submitted (any JSON structure)

Response:
- If verification is required:
  \`\`\`json
  {
    "message": "Verification code sent to user@example.com",
    "verification_id": "uuid-here",
    "requires_verification": true
  }
  \`\`\`

- If verification is not required:
  \`\`\`json
  {
    "success": true,
    "message": "Data submitted successfully",
    "id": "inserted-id-here"
  }
  \`\`\`

#### 2. Verify and Submit

\`\`\`
POST /api/verify-submit/
\`\`\`

Request body:
\`\`\`json
{
  "verification_code": "ABC123",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword",
    "custom_field": "custom value"
  }
}
\`\`\`

Response:
\`\`\`json
{
  "success": true,
  "message": "Data submitted successfully",
  "id": "inserted-id-here"
}
\`\`\`

#### 3. Request Password Reset

\`\`\`
POST /api/password-reset/request/
\`\`\`

Request body:
\`\`\`json
{
  "email": "user@example.com"
}
\`\`\`
OR
\`\`\`json
{
  "phone": "+1234567890"
}
\`\`\`

Response:
\`\`\`json
{
  "message": "Password reset code sent to user@example.com",
  "verification_id": "uuid-here"
}
\`\`\`

#### 4. Verify Password Reset and Set New Password

\`\`\`
POST /api/password-reset/verify/
\`\`\`

Request body:
\`\`\`json
{
  "email": "user@example.com",
  "verification_code": "ABC123",
  "new_password": "newSecurePassword"
}
\`\`\`
OR
\`\`\`json
{
  "phone": "+1234567890",
  "verification_code": "ABC123",
  "new_password": "newSecurePassword"
}
\`\`\`

Response:
\`\`\`json
{
  "success": true,
  "message": "Password updated successfully"
}
\`\`\`

## Admin Interface

Access the admin interface at `/admin/` to:
- Register companies
- Configure database connections
- Set up email templates and SMTP/API settings
- Set up SMS templates and provider settings
- Define validation rules
- View API logs

## Company Setup

1. Create a company in the admin interface
2. Configure database connection details
3. Set up email templates and email provider settings (optional)
4. Set up SMS templates and provider settings (optional)
5. Define validation rules (optional)
6. Use the provided API key in your frontend

## Email Configuration

Companies can choose between:

### SMTP-based Email
- Configure SMTP host, port, username, password, and TLS settings
- Suitable for traditional email servers like Gmail, Outlook, etc.

### API-based Email
- Configure API key and other required settings
- Supported providers:
  - **SendGrid**: Requires API key
  - **Mailgun**: Requires API key and domain
  - **Postmark**: Requires API key
  - **Amazon SES**: Requires AWS access key, secret key, and region

## Verification Methods

Companies can choose between:
1. **Email Verification**: Sends a 6-digit alphanumeric code to the user's email
2. **Phone Verification**: Sends a 6-digit alphanumeric code via SMS
3. **No Verification**: Directly stores the user data without verification

## SMS Providers

The system supports the following SMS providers:
1. **Twilio**: Requires account SID, auth token, and from number
2. **Nexmo/Vonage**: Requires API key, API secret, and from name
3. **AWS SNS**: Requires AWS access key, secret key, region, and sender ID

## Validation Rules

Validation rules are defined as a JSON object where each key is a field name and the value is an object with validation rules:

\`\`\`json
{
  "email": {
    "required": true,
    "type": "email"
  },
  "name": {
    "required": true,
    "min_length": 2,
    "max_length": 100
  },
  "age": {
    "type": "number",
    "custom_validator": "def validate_custom(value): return True if value >= 18 else 'Must be at least 18 years old'"
  }
}
\`\`\`

## Email and SMS Templates

Templates support the following placeholders:
- `{{name}}`: User's name
- `{{code}}`: Verification code
- Any other field from the form data can be used as a placeholder

## Security Considerations

- API keys should be kept secure
- Database credentials are encrypted in the database
- Rate limiting is applied to prevent abuse
- Validation rules help prevent malicious data
- Passwords are securely hashed using bcrypt
