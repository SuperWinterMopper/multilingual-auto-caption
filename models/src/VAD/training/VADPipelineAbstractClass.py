from ...common.PipelineStructure import ModelPipeline, PipelineLogger, PipelineTester
from pathlib import Path

class VADPipelineAbstractClass(ModelPipeline):
    tester: PipelineTester
    logger: PipelineLogger

    data_path: Path