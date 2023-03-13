

class Model(object):
    def reply(self,query,context =None):
        """
        model auto-reply content
        :param req: received message
        :return: reply content
        """
        raise NotImplementedError