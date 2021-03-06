"""utils.py - File for collecting general utility functions."""

# have to do these sys.path.inserts when running unit tests that call utils.py
# import sys
# sys.path.insert(1, '/usr/local/google_appengine')
# sys.path.insert(1, '/usr/local/google_appengine/lib/endpoints-1.0')
# sys.path.insert(1, '/usr/local/google_appengine/lib/protorpc-1.0')
# sys.path.insert(1, '/usr/local/google_appengine/lib/yaml/lib')

from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity
