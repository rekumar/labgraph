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
import Api from '../api/api';


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

    const carouselContent = {
        height: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column' as 'column',
        backgroundColor: theme.colors.yellow[5],
        borderRadius: 15,
        gap: 15
    };

    return (
        <section id="section-one">
            <Space h="xl" />

            <Container fluid={true}>
                <TabbedTables />


                {/* <Text color="black" align="center" mb="15px">
                    <Title order={1}>Explain something in this carousel</Title>
                </Text>

                <Text color="black" align="center" mb="25px">
                    You can insert images or some texts if you need.
                </Text>

                <Carousel
                    withIndicators
                    height={300}
                    slideSize="33.333333%"
                    slideGap="md"
                    breakpoints={[
                        { maxWidth: 'md', slideSize: '50%' },
                        { maxWidth: 'sm', slideSize: '100%', slideGap: 15 },
                    ]}
                    loop
                    align="start"
                    pr="10px"
                    pl="10px"
                >
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>1</Title>
                            <Text>Write something here.</Text>
                        </div>
                    </Carousel.Slide>
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>2</Title>
                            <Text>Something here too.</Text>
                        </div>
                    </Carousel.Slide>
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>3</Title>
                            <Text>Mh, maybe here too?</Text>
                        </div>
                    </Carousel.Slide>
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>4</Title>
                            <Text>If you'd like to you could do that here...</Text>
                        </div>
                    </Carousel.Slide>
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>5</Title>
                            <Text>Woah, you are quite convincing..</Text>
                        </div>
                    </Carousel.Slide>
                    <Carousel.Slide>
                        <div style={carouselContent}>
                            <Title order={2}>6</Title>
                            <Text>And we are done with the cards!</Text>
                        </div>
                    </Carousel.Slide>
                </Carousel> */}
            </Container>
        </section>
    );
};

export default Tables;