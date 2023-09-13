from dataclasses import dataclass

@dataclass
class folder_annotations(): 
    consortium: str
    folderType: str
    dataType: str
    species: str
    study: str
    assay: str

    def __init__(self,consortium, folderType, dataType, species, study, assay): 
        self.consortium = consortium
        self.folderType = folderType
        self.dataType = dataType
        self.species = species
        self.study = study
        self.assay = assay
    
    def create_annotations(self): 
        """Create annotation dictionary to upload with folder

        Returns:
            dictionary: dictionary of the base folder annotations
        """
        self.ants = {
            'folderType': self.folderType,
            'consortium': self.consortium,
            'dataType': self.dataType,
            'species': self.species,
            'study': self.study,
            'assay': self.assay
        }
        return self.ants
    def add_annotation(self, d):
        """add a new annotation to the folder class

        Args:
            d (dict): dictionary 
        """

        self.ants = self.ants | d
