import React from "react";
import ReactDOM from "react-dom";
import {addDataHookListener} from "../utils";
import PeopleList from "./people-list";

addDataHookListener("people-list", "context", PeopleList);
