from rest_framework import serializers

def validate_data(data, validation_rules):
    """Validate data against company-specific validation rules"""
    errors = {}
    
    # Check if password and confirm_password match
    if 'password' in data and 'confirm_password' in data:
        if data['password'] != data['confirm_password']:
            errors['confirm_password'] = ['Passwords do not match.']
    elif 'password' in data and 'confirm_password' not in data:
        errors['confirm_password'] = ['Confirm password is required.']
    
    for field, rules in validation_rules.items():
        if field in data:
            value = data[field]
            
            # Required field
            if rules.get('required', False) and (value is None or value == ''):
                errors[field] = ['This field is required.']
                continue
            
            # Skip validation if field is empty and not required
            if value is None or value == '':
                continue
            
            # Type validation
            field_type = rules.get('type')
            if field_type:
                if field_type == 'string' and not isinstance(value, str):
                    errors[field] = [f'Must be a string.']
                elif field_type == 'number' and not (isinstance(value, int) or isinstance(value, float)):
                    errors[field] = [f'Must be a number.']
                elif field_type == 'boolean' and not isinstance(value, bool):
                    errors[field] = [f'Must be a boolean.']
                elif field_type == 'email':
                    # Simple email validation
                    if not isinstance(value, str) or '@' not in value:
                        errors[field] = [f'Must be a valid email address.']
            
            # Min length validation
            min_length = rules.get('min_length')
            if min_length and isinstance(value, str) and len(value) < min_length:
                errors[field] = [f'Must be at least {min_length} characters.']
            
            # Max length validation
            max_length = rules.get('max_length')
            if max_length and isinstance(value, str) and len(value) > max_length:
                errors[field] = [f'Must be at most {max_length} characters.']
            
            # Pattern validation
            pattern = rules.get('pattern')
            if pattern and isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    errors[field] = [f'Does not match the required pattern.']
            
            # Custom validation function
            custom_validator = rules.get('custom_validator')
            if custom_validator:
                try:
                    # Execute custom validation function
                    exec(custom_validator)
                    validate_custom = locals()['validate_custom']
                    result = validate_custom(value)
                    if result is not True:
                        errors[field] = [result]
                except Exception as e:
                    errors[field] = [f'Custom validation error: {str(e)}']
        
        elif rules.get('required', False):
            errors[field] = ['This field is required.']
    
    if errors:
        raise serializers.ValidationError(errors)
    
    return True
