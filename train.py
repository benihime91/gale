import hydra
from omegaconf import DictConfig, OmegaConf


@hydra.main(config_path="gale/hydra")
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    main()