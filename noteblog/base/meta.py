class Meta:
    def __init__(self, *args, **kwargs):
        pass

    def to_dict(self):
        res = {}
        res.update(self.__dict__)
        return res


class Cate(Meta):
    def __init__(self, *args, **kwargs):
        super(Cate, self).__init__(*args, **kwargs)


class Page(Meta):
    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        pass
