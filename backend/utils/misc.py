def singleton(cls):
    """Décorateur pour s'assurer que la classe est instanciée une seule fois."""
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance