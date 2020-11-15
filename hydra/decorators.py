def register(model):
    """
    Register the given model(s) classes and wrapped ModelSite class:
    @register(Author)
    class AuthorSite(hydra.ModelSite):
        pass
    """
    from hydra import ModelSite, site

    def _model_site_wrapper(site_class):
        if not model:
            raise ValueError('One model must be passed to register.')

        if not issubclass(site_class, ModelSite):
            raise ValueError('Wrapped class must subclass ModelSite.')

        site.register(model, site_class=site_class)

        return site_class
    return _model_site_wrapper