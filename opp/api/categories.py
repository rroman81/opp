import base_handler
from opp.db import api, models
from opp.common import aescipher


class ResponseHandler(base_handler.BaseResponseHandler):

    def _handle_getall(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        with api.get_session() as session:
            categories = api.category_getall(session=session)
            for category in categories:
                cat = cipher.decrypt(category.blob)
                response.append({'id': category.id, 'category': cat})

        return {'result': 'success', 'categories': response}

    def _handle_create(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        categories = []
        for cat in cat_list:
            if not cat:
                resp = {'category': None,
                        'status': "empty category not allowed"}
            else:
                # Encrypt category name blob and append to list
                blob = cipher.encrypt(cat)
                categories.append(models.Category(blob=blob))
                resp = {'category': cat, 'status': "success: created"}

            payload.append(resp)

        with api.get_session() as session:
            api.category_create_update(categories, session=session)

        return {'result': 'success', 'payload': payload}

    def _handle_update(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        categories = []
        for cat in cat_list:
            if not cat:
                # Silently ignore any empty dictionaries
                continue
            try:
                # Make sure category id is parsed from request
                cat_id = cat['id']
            except KeyError:
                cat_id = None

            if not cat_id:
                cat['status'] = "error: missing or empty category id"
            else:
                try:
                    # Make sure category is parsed from request
                    category = cat['category']
                except KeyError:
                    category = None

                if not category:
                    cat['status'] = "error: missing or empty category"
                else:
                    blob = cipher.encrypt(cat)
                    categories.append(models.Category(blob=blob))
                    cat['status'] = "success: updated"

            payload.append(cat)

        with api.get_session() as session:
            api.category_create_update(categories, session=session)

        return {'result': 'success', 'payload': payload}

    def _handle_delete(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        payload = []
        categories = []
        for cat_id, cascade in cat_list:
            if not cat_id:
                resp = {'id': None, 'status': "error: empty category id"}
            else:
                categories.append(cat_id)
                resp = {'id': cat_id, 'status': "success: deleted"}

                if cascade is True:
                    pass
                    # TODO(alex_bash): delete associated entries
                else:
                    pass
                    # TODO(alex_bash): clear category in associated entries

            payload.append(resp)

        with api.get_session() as session:
            api.category_delete(categories, session=session)

        return {'result': 'success', 'payload': payload}
