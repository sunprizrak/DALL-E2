from kivy.network.urlrequest import UrlRequest
import json
from settings import storage, host_name


class OpenAIController:
    path_image_generation = host_name + 'openai/image_generation/'
    path_image_edit = host_name + 'openai/image_edit/'
    path_image_variation = host_name + 'openai/image_variation/'
    path_text_completion = host_name + 'openai/text_completion/'

    def image_generation(self, prompt, image_count, image_size, callback, error, failure):
        token = storage.get('auth_token').get('token')

        UrlRequest(
            url=self.path_image_generation,
            method='GET',
            on_success=callback,
            on_error=error,
            on_failure=failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )

    def image_edit(self, image, mask, prompt, image_count, image_size, callback, on_error, on_failure):
        token = storage.get('auth_token').get('token')

        UrlRequest(
            url=self.path_image_edit,
            method='GET',
            on_success=callback,
            on_error=on_error,
            on_failure=on_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'image': image, 'mask': mask, 'prompt': prompt, 'image_count': image_count, 'image_size': image_size}),
        )

    def image_variation(self, image, image_count, image_size, callback, on_error, on_failure):
        token = storage.get('auth_token').get('token')

        UrlRequest(
            url=self.path_image_variation,
            method='GET',
            on_success=callback,
            on_error=on_error,
            on_failure=on_failure,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'image': image, 'image_count': image_count, 'image_size': image_size}),
        )

    def text_completion(self, prompt, callback):
        token = storage.get('auth_token').get('token')

        UrlRequest(
            url=self.path_text_completion,
            method='GET',
            on_success=callback,
            req_headers={
                'Content-type': 'application/json',
                'Authorization': f"Token {token}",
            },
            req_body=json.dumps({'prompt': prompt}),
        )