import logging


logger = logging.getLogger(__name__)


class DatabaseResetService:
    def __init__(self, device_repository, telemetry_repository):
        self.device_repository = device_repository
        self.telemetry_repository = telemetry_repository

    def clear_all_data(self):
        telemetry_deleted = self.telemetry_repository.delete_all()
        devices_deleted = self.device_repository.delete_all()

        logger.info(
            "Database reset completed telemetry_deleted=%s devices_deleted=%s",
            telemetry_deleted,
            devices_deleted,
        )
        return {
            "telemetry_deleted": telemetry_deleted,
            "devices_deleted": devices_deleted,
        }
