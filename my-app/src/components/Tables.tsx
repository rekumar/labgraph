import { Container, useMantineTheme, Tabs, Space } from '@mantine/core';
import { SampleTable } from './Tables/Samples';
import { samples } from '../__mock__/samples';
import { ActionsTable } from './Tables/Actions';
import { actions } from '../__mock__/actions';
import { AnalysesTable } from './Tables/Analyses';
import { analyses } from '../__mock__/analyses';
import { MaterialsTable } from './Tables/Materials';
import { materials } from '../__mock__/materials';
import { measurements } from '../__mock__/measurements';
import { MeasurementsTable } from './Tables/Measurements';
import { actors } from '../__mock__/actors';
import { ActorsTable } from './Tables/Actors';
import { analysis_methods } from '../__mock__/analysis_methods';
import { AnalysisMethodsTable } from './Tables/AnalysisMethods';
import React from 'react';


function TabbedTables() {
    return (
        <Tabs
            defaultValue="samples"
            variant="pills"
        >
            <Tabs.List position="center">
                <Tabs.Tab value="samples">Samples</Tabs.Tab>
                <Tabs.Tab value="materials">Materials</Tabs.Tab>
                <Tabs.Tab value="actions">Actions</Tabs.Tab>
                <Tabs.Tab value="measurements">Measurements</Tabs.Tab>
                <Tabs.Tab value="analyses">Analyses</Tabs.Tab>
                <Tabs.Tab value="actors">Actors</Tabs.Tab>
                <Tabs.Tab value="analysis_methods">Analysis Methods</Tabs.Tab>
            </Tabs.List>

            <Space h="sm" />
            <Tabs.Panel value="samples">
                <SampleTable />
            </Tabs.Panel>
            <Tabs.Panel value="materials">
                <MaterialsTable data={materials} />
            </Tabs.Panel>
            <Tabs.Panel value="actions">
                <ActionsTable data={actions} />
            </Tabs.Panel>
            <Tabs.Panel value="analyses">
                <AnalysesTable data={analyses} />
            </Tabs.Panel>
            <Tabs.Panel value="measurements">
                <MeasurementsTable data={measurements} />
            </Tabs.Panel>
            <Tabs.Panel value="actors">
                <ActorsTable data={actors} />
            </Tabs.Panel>
            <Tabs.Panel value="analysis_methods">
                <AnalysisMethodsTable data={analysis_methods} />
            </Tabs.Panel>
        </Tabs>
    )
}
const Tables = () => {
    const theme = useMantineTheme();

    return (
        <section id="section-one">
            <Space h="xl" />

            <Container fluid={true}>
                <TabbedTables />

            </Container>
        </section>
    );
};

export default Tables;