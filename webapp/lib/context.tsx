"use client";

import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { getOrganizations, Organization } from "./api";

interface OrgContextType {
    selectedOrg: string;
    setSelectedOrg: (org: string) => void;
    organizations: Organization[];
    refreshOrgs: () => Promise<void>;
}

const OrgContext = createContext<OrgContextType | undefined>(undefined);

export function OrgProvider({ children }: { children: ReactNode }) {
    const [selectedOrg, setSelectedOrg] = useState("default_org");
    const [organizations, setOrganizations] = useState<Organization[]>([
        { id: "default_org", name: "Internal (Default)", slug: "default_org" }
    ]);

    const refreshOrgs = async () => {
        try {
            const orgs = await getOrganizations();
            if (orgs.length > 0) {
                setOrganizations(orgs);
                // If current selected isn't in new list, pick first one
                if (!orgs.find(o => o.slug === selectedOrg)) {
                    setSelectedOrg(orgs[0].slug);
                }
            }
        } catch (error) {
            console.error("Failed to fetch organizations:", error);
        }
    };

    useEffect(() => {
        refreshOrgs();
    }, []);

    return (
        <OrgContext.Provider value={{ selectedOrg, setSelectedOrg, organizations, refreshOrgs }}>
            {children}
        </OrgContext.Provider>
    );
}

export function useOrg() {
    const context = useContext(OrgContext);
    if (context === undefined) {
        throw new Error("useOrg must be used within an OrgProvider");
    }
    return context;
}
