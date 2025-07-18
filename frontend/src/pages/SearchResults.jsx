import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import AsidePanel from '../components/AsidePanel';
import Card from '../components/Card';
import { fetchSearchResults } from '../api/crypta';

const useQuery = () => {
    return new URLSearchParams(useLocation().search);
};

const SearchResults = () => {
    const query = useQuery();
    const [results, setResults] = useState([]);

    useEffect(() => {
        const q = query.get('q');
        fetchSearchResults(q).then(res => setResults(res.data.results));
    }, [query]);

    return (
        <div className="container-fluid search-page">
            <div className="row">
                <AsidePanel header="Actions">
                    {/* Todo: Action Buttons */}
                </AsidePanel>
                <main className="col-md-8 p-4 bg-light">
                    <Card title="Search Results">
                        {data.persons.length > 0 && (
                        <>
                            <h5 className="mt-4">People</h5>
                            <ul className="list-group mb-3">
                                {data.persons.map(p => (
                                    <li className="list-group-item" key={p.id}>
                                        <Link to={`/details/person/${p.id}`}>{p.name}</Link>
                                    </li>
                                ))}
                            </ul>
                        </>
                        )}
                        {data.locations.length > 0 && (
                        <>
                            <h5 className="mt-4">Locations</h5>
                            <ul className="list-group mb-3">
                                {data.persons.map(l => (
                                    <li className="list-group-item" key={l.id}>
                                        <Link to={`/details/person/${l.id}`}>{l.name}</Link>
                                    </li>
                                ))}
                            </ul>
                        </>
                        )}
                    </Card>
                </main>
            </div>
        </div>
    );
};

export default SearchResults;
