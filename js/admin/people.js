import React from "react";
import {addDataHookListener} from "../utils";
import PeopleList from "./people-list";
import NewPersonForm from "./add-person";
import DuplicateSponsors from "./duplicate-sponsors";

addDataHookListener("people-list", "context", PeopleList);
addDataHookListener("new-person", "context", NewPersonForm);
addDataHookListener("duplicate-sponsors", "context", DuplicateSponsors);
