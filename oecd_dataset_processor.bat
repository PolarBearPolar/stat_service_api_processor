@echo off
set dataset_id=MSTI_PUB
set host_work_dir=C:\Users\User\Desktop\Docker\mount
set save_mode=xlsx
docker run -it ^
-e DATASET_ID=%dataset_id% ^
-e HOST_WORK_DIR=%host_work_dir% ^
-e SAVE_MODE=%save_mode% ^
-p 8080:8080 ^
-v %host_work_dir%:/home/oecd_dataset_processor/output ^
oecd_dataset_processor:0.1