import requests
from config import main_url


def work_service():
    rez = requests.get(main_url)
    if rez.status_code == 200:
        return True
    else:
        raise Exception('Service not started')


def create_true_post(data):

    rez = requests.post(url=main_url + 'posts', json=data)
    if rez.status_code == 201:
        rez_json = rez.json()
        post_id = rez_json['id']
        rez_json.pop('id')
        if data == rez_json:
            return post_id
        else:
            raise Exception('Failed response')
    else:
        print(rez.status_code)
        raise Exception('Failed status code')


def create_false_post():
    data = {
        "title": "test_post",
        "body": "test_body",
        "author": "",
        "created_at": 1141241
    }

    rez = requests.post(url=main_url + 'posts', json=data)
    if rez.status_code == 400:
        return True
    else:
        raise Exception('Failed status code')


def edit_true_post(data, post_id):
    rez = requests.put(url=main_url + f'posts/{post_id}', json=data)
    if rez.status_code == 200:
        rez_json = rez.json()
        post_id = rez_json['id']
        rez_json.pop('id')
        if data == rez_json:
            return post_id
        else:
            raise Exception('Failed response')
    else:
        raise Exception('Failed status code')


def delete_post(post_id):
    rez = requests.delete(url=main_url + f'posts/{post_id}')
    if rez.status_code == 204:
        return True
    else:
        raise Exception('Failed status code')


def get_post(post_id, data_to_check):
    rez = requests.get(url=main_url + f'posts/{post_id}')
    if rez.status_code == 200:
        rez_json = rez.json()
        if rez_json == data_to_check:
            return True
    else:
        raise Exception('Failed status code')


if __name__ == '__main__':
    work_service()
    data = {
        "title": "test_post",
        "body": "test_body",
        "author": "Root",
        "created_at": "2019-09-20T07:12:52.581Z"
    }
    post_id1 = create_true_post(data)
    create_false_post()
    data = {
        "title": "test_post2",
        "body": "test_body2",
        "author": "Bob",
        "created_at": "2019-09-20T07:12:52.581Z"
    }
    post_id2 = create_true_post(data)
    data = {
        "title": "test_post_edit",
        "body": "test_body_edit",
        "author": "Root",
        "created_at": "2019-09-20T07:12:52.581Z"
    }
    post_id1 = edit_true_post(data, post_id1)
    delete_post(post_id2)
    data['id'] = post_id1
    get_post(post_id1, data)


