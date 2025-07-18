import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import '../styles/Details.css';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import PersonPrimaryInfo from '../components/PersonPrimaryInfo';
import ContactInfo from '../components/ContactInfo';
import BirthInfo from '../components/BirthInfo';
import StandingInfo from '../components/StandingInfo';
import DegreeInfo from '../components/DegreeInfo';
import FormationInfo from '../components/FormationInfo';
import NameInfo from '../components/NameInfo';
import EmergencyInfo from '../components/EmergencyInfo';
import LocationPrimaryInfo from '../components/LocationPrimaryInfo';
import LocationInfo from '../components/LocationInfo';
import ClergyInfo from '../components/ClergyInfo';
import MassInfo from '../components/MassInfo';
import StaffInfo from '../components/StaffInfo';
import StatisticsInfo from '../components/StatisticsInfo';
import Modal from '../components/Modal';
import { fetchDetails } from '../api/crypta';
import Chart from 'chart.js/auto';

const Details = () => {
    const { base, id } = useParams();
    const [data, setData] = useState(null);

    useEffect(() => {
        fetchDetails(base, id).then(res => setData(res.data));
    }, [base, id]);

    if (!data) return <div>Loading...</div>;

    const sidebarLinks = data.sidebarLinks || [
        { target: 'primary-info', label: 'Primary Info' },
        // additional sections
    ];

    const renderSidebar = () => {
        <AsidePanel header="Sections">
            <nav className="nav flex-column px-3 mb-auto">
                {sidebarLinks.map(link => (
                    <a
                        key={link.target}
                        href="#"
                        className="nav-link"
                        onClick={e => { e.preventDefault(); document.getElementById(link.target).scrollIntoView();}}
                    >
                        {link.label}
                    </a>
                ))}
            </nav>
        </AsidePanel>
    };

    const renderOffertoryChart = () => {
        useEffect(() => {
        const ctx = document.getElementById('offertoryChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
            labels: data.offertories.map(o => o.year),
            datasets: [{ label: 'Offertory', data: data.offertories.map(o => o.income) }],
            },
        });
        }, [data.offertories]);

        return (
        <Card title="Offertory Income Over Years">
            <canvas id="offertoryChart" />
        </Card>
        );
    };

    return (
        <div className="container-fluid details-page">
        <div className="row">
            {renderSidebar()}
            <main className="col-md-8 p-4 bg-light">
                {base === 'person' ? (
                    <>
                        <PersonPrimaryInfo
                        assignments={data.assignments}
                        statuses={data.statuses}
                        />
                        <ContactInfo
                            emails={data.emails}
                            phones={data.phones}
                            residence={data.residence}
                            mailing={data.mailing}
                            />
                        <BirthInfo
                            dateOfBirth={data.date_birth}
                            birthPlace={data.person_details?.birth_city + ', ' + data.person_details?.birth_state + ' ' + data.person_details?.birth_country}
                            baptismDate={data.date_baptism}
                            baptismPlace={data.person_details?.lkp_placeOfBaptism_id?.name}
                            />
                        <StandingInfo statuses={data.statuses.map(s => ({ id: s.id, name: s.lkp_status_id.name, date_assigned: s.date_assigned, date_released: s.date_released }))} />
                        <DegreeInfo
                            degrees={data.degrees.map(d => ({ id: d.id, institute: d.lkp_degreeCertificate_id.institute, subject: d.lkp_degreeCertificate_id.lkp_subjectMatter_id.name, degreeType: d.lkp_degreeCertificate_id.lkp_typeOfDegree_id.name, dateAcquired: d.date_acquired, dateExpiration: d.date_expiration }))}
                            languages={data.languages.map(l => ({ id: l.id, name: l.lkp_language_id.name, proficiency: l.lkp_languageProficiency_id.name }))}
                            otherSkills={data.person_details?.otherSkillsCompentencies}
                            />
                        <FormationInfo formationDates={{
                            TransitionalDiaconateOrdination: data.person_details?.date_transitionalDiaconateOrdination,
                            PriestOrdination: data.person_details?.date_priestOrdination,
                            EpiscopalOrdination: data.person_details?.date_episcopalOrdination,
                            Incardination: data.person_details?.date_incardination
                            }} />
                        <NameInfo prefix={data.prefix} 
                            first={data.name_first} 
                            middle={data.name_middle} 
                            last={data.name_last} 
                            suffix={data.suffix}
                            religiousSuffix={data.person_details.religiousSuffix}
                            diocesanSuffix={data.person_details.diocesanSuffix} 
                            />
                        <EmergencyInfo
                            contacts={data.relationships
                            .filter(rel => rel.is_emergencyContact)
                            .map(rel => ({
                            id: rel.id,
                            relationshipType: rel.lkp_relationshipType_id.name,
                            name: rel.lkp_secondPerson_id.name,
                            address: rel.lkp_secondPerson_id.lkp_residence_id
                                ? `${rel.lkp_secondPerson_id.lkp_residence_id.address1}, ${rel.lkp_secondPerson_id.lkp_residence_id.city}, ${rel.lkp_secondPerson_id.lkp_residence_id.state}`
                                : null,
                            phone1: rel.lkp_secondPerson_id.person_phone_set[0]?.phoneNumber,
                            phone2: rel.lkp_secondPerson_id.person_phone_set[1]?.phoneNumber,
                            email1: rel.lkp_secondPerson_id.person_email_set[0]?.email,
                            email2: rel.lkp_secondPerson_id.person_email_set[1]?.email,
                            }))
                        }
                        />
                    </>
                ) : (
                    <>
                        <LocationPrimaryInfo
                            details={data.details}
                            statuses={data.statuses}
                            />
                        <LocationInfo
                            physical={`${data.lkp_physicalAddress_id.address1}, ${data.lkp_physicalAddress_id.city}`}
                            mailing={`${data.lkp_mailingAddress_id.address1}, ${data.lkp_mailingAddress_id.city}`}
                            rectory={`${data.location_details.lkp_rectoryAddress.address1}, ${data.location_details.lkp_rectoryAddress.city}`}
                            />
                        <ClergyInfo 
                            clergy={data.active_assignments.map(a => ({ 
                                id: a.lkp_person_id.pk, 
                                name: a.lkp_person_id.name, 
                                role: a.lkp_assignmentType_id.title 
                            }))} 
                            />
                        <MassInfo 
                            masses={data.languages} 
                            octoberCounts={data.october_counts} 
                            />
                        <StaffInfo animarum={data.statusAnimarum.last || {}} />
                        <StatisticsInfo statData={data.statusAnimarum} />
                    </>
                )};
                
            {/* Additional sections go here... */}

            {data.offertories && renderOffertoryChart()}
            </main>
        </div>

        {/* Actions Modal */}
        <Modal id="actionModal" title="Actions">
            <div className="d-grid gap-2">
            {base === 'person' ? (
                <button className="btn result-btn btn-sm">Report: Assignment History</button>
            ) : (
                <>
                <button className="btn result-btn btn-sm">Report: P3 Report</button>
                <button className="btn result-btn btn-sm">Report: Status Animarum</button>
                <button className="btn result-btn btn-sm">Report: Offertories</button>
                </>
            )}
            </div>
        </Modal>
        </div>
    );
};

export default Details;
