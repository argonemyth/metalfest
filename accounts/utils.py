import json

def errors_to_dict(errors):
    """
    Turn form errors to dictionary.
    """
    data = {}
    for key, value in errors.iteritems():
        data['id_' + key] = [v for v in value]
    return data

def errors_to_json(errors, status=False):
    if not status:
        return json.dumps(errors_to_dict(errors))
        
    error_dict = errors_to_dict(errors)
    error_dict['status'] = 'errors' 
    return json.dumps(error_dict) 

# def get_facebook_avatar(fb_id):
#  url = "http://graph.facebook.com/%s/picture?type=large" % fb_id 
#  return url
