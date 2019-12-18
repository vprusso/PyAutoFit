from autofit.tools.phase import Dataset


class MockDataset(Dataset):
    @property
    def name(self) -> str:
        return "name"


def test_save_and_load():
    dataset = MockDataset()
    dataset.save("/tmp")
    assert dataset.name == MockDataset.load(f"/tmp/{dataset.name}.pickle").name