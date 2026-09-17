import app.main as core
from app.professional_dashboard import ProfessionalDashboardPage


# Keep the existing application services and database logic, while swapping
# only the dashboard presentation layer at startup.
core.DashboardPage = ProfessionalDashboardPage


if __name__ == "__main__":
    raise SystemExit(core.main())
