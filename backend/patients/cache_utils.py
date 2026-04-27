from constance import config
from django.core.cache import cache


def patient_list_cache_key(user_id):
    return f"patients:list:{user_id}"


def patient_detail_cache_key(user_id, patient_id):
    return f"patients:detail:{user_id}:{patient_id}"


def get_cached_patient_list(user_id):
    return cache.get(patient_list_cache_key(user_id))


def set_cached_patient_list(user_id, data):
    cache.set(
        patient_list_cache_key(user_id),
        data,
        timeout=config.PATIENT_LIST_CACHE_TIMEOUT,
    )


def get_cached_patient_detail(user_id, patient_id):
    return cache.get(patient_detail_cache_key(user_id, patient_id))


def set_cached_patient_detail(user_id, patient_id, data):
    cache.set(
        patient_detail_cache_key(user_id, patient_id),
        data,
        timeout=config.PATIENT_LIST_CACHE_TIMEOUT,
    )


def invalidate_patient_cache(user_id, patient_id=None):
    cache.delete(patient_list_cache_key(user_id))
    if patient_id is not None:
        cache.delete(patient_detail_cache_key(user_id, patient_id))
