import { useState } from 'react'
import './PreviousRunCard.css'

function PreviousRunCard() {
    
    
    return (
        <div className="wrapper">
        <header className="Title">
            LCCDE
        </header>

        <div className="middleItems">
            <p>F1-SCORE: </p>
            <p>Execution Time: </p>
        </div>
        <div className="bottomItem">
            <p>Date: </p>
        </div>
        
        </div>
    )
}

export default PreviousRunCard