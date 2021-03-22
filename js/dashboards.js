import AccountsOverview from "./account-overview";
import APIDashboard from "./api-dashboard";
import { addDataHookListener } from "./utils";

addDataHookListener("account-overview", "context", AccountsOverview);
addDataHookListener("api-dashboard", "context", APIDashboard);
