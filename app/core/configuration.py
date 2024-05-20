from omegaconf import DictConfig, OmegaConf
from app.utils.logging_helper import logger
import sys
from hydra import compose, initialize
from pathlib import Path

class AppConfig:
    def __init__(self, cfg_path: DictConfig):
        self.cfg_path = cfg_path


    def load_config(self) -> DictConfig:
        try:
            # Get environment name
            env = self.cfg_path
            
            # Init omegaconfig
            with initialize(version_base=None, config_path="../../config/", job_name=env):
                # Load common configuration
                logger.info('Loading common config')
                common_cfg = OmegaConf.load('./config/common.yaml')
                
                # Load environment-specific configuration
                logger.info(f'Loading {env} config')
                env_cfg = None # Init a env_cfg variable
                if env == "staging":
                    env_cfg = compose(config_name="staging")
                elif env == "prod":
                    env_cfg = compose(config_name="production")
                elif env == "dev":
                    env_cfg = compose(config_name="development")
                else:
                    env_cfg = compose(config_name="test")

                # Merge common configuration with environment-specific configuration
                logger.info(f'Merging common and {env} configs into one')
                final_cfg = OmegaConf.merge(common_cfg, env_cfg)
                logger.info("Config merged successfully")

            return OmegaConf.create(final_cfg)
        except FileNotFoundError:
            logger.error(f"Error: Configuration file '{self.cfg_path}' not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            sys.exit(1)
            