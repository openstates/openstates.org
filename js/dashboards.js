import AccountsOverview from "./account-overview";
import APIDashboard from "./api-dashboard";

addDataHookListener("account-overview", "context", AccountsOverview);
addDataHookListener("api-dashboard", "context", APIDashboard);
