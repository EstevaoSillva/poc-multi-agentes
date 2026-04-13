from agno.tools import Toolkit

class AuditedTool(Toolkit):
    def __init__(self, tool, logger):
        self._tool = tool
        self._logger = logger
        self.name = tool.name
        self.description = getattr(tool, "description", "")

    def run(self, **kwargs):
        output = self._tool.run(**kwargs)

        self._logger.record(
            name=self.name,
            input_payload=kwargs,
            output_payload=output
        )

        return output
