import React from "react";
import {addDataHookListener} from "../utils";
import PeopleList from "./people-list";
import NewPersonForm from "./add-person";

addDataHookListener("people-list", "context", PeopleList);
addDataHookListener("new-person", "context", NewPersonForm);
