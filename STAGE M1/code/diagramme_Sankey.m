%% ==========================================
% PARTIE FC : CALCUL ET EXPORT
% ==========================================
% Consensus par groupe pour FC
D1_FC = agreement(Ci_FC(find(groups==1), :)') / sum(groups==1);
Ci_FC_G1 = consensus_und(D1_FC, tau, reps);

D2_FC = agreement(Ci_FC(find(groups==2), :)') / sum(groups==2);
Ci_FC_G2 = consensus_und(D2_FC, tau, reps);

D3_FC = agreement(Ci_FC(find(groups==3), :)') / sum(groups==3);
Ci_FC_G3 = consensus_und(D3_FC, tau, reps);

% Export FC
T_FC = table(Ci_FC_G1, Ci_FC_G2, Ci_FC_G3, 'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_FC, 'sankey_data_FC.csv');
fprintf('Fichier sankey_data_FC.csv enregistré !\n');

%% ==========================================
% PARTIE SC : CALCUL ET EXPORT
% ==========================================
% Consensus par groupe pour SC
D1_SC = agreement(Ci_SC(find(groups==1), :)') / sum(groups==1);
Ci_SC_G1 = consensus_und(D1_SC, tau, reps);

D2_SC = agreement(Ci_SC(find(groups==2), :)') / sum(groups==2);
Ci_SC_G2 = consensus_und(D2_SC, tau, reps);

D3_SC = agreement(Ci_SC(find(groups==3), :)') / sum(groups==3);
Ci_SC_G3 = consensus_und(D3_SC, tau, reps);

% Export SC
T_SC = table(Ci_SC_G1, Ci_SC_G2, Ci_SC_G3, 'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_SC, 'sankey_data_SC.csv');
fprintf('Fichier sankey_data_SC.csv enregistré !\n');