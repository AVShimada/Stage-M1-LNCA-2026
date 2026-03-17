%% ========================================================================
%  ANALYSE MULTIMODALE (ALLÉGEANCE) SUR SUBJECT_1
%% ========================================================================

SUBJECT = SUBJECT_1; 
FC = SUBJECT.FC; FC(1:N_nodes+1:end) = 0;
SC = SUBJECT.SC; SC(1:N_nodes+1:end) = 0;
SC_log = log(SC + 1);

modes = {'FC','Log-SC'};
data_cell = {FC, SC_log};

P_all = cell(1,2);
Mat_sorted_all = cell(1,2);

for m = 1:length(modes)
    
    current_data = data_cell{m};
    fprintf('\n--- Allégeance : %s ---\n', modes{m});
    
    Ci_runs = zeros(n_runs, N_nodes);
    
    for r = 1:n_runs
        
        if strcmp(modes{m}, 'FC')
            [Ci, ~] = community_louvain(current_data, gamma, [], 'negative_sym');
        else
            [Ci, ~] = community_louvain(current_data, gamma);
        end
        
        Ci_runs(r,:) = Ci;
        
    end
    
    P = agreement(Ci_runs') / n_runs;
    P_all{m} = P;
    
    % Tri par consensus du sujet 1
    if strcmp(modes{m}, 'FC')
        Ci_ref = Ci_FC(1,:)';
    else
        Ci_ref = Ci_SC(1,:)';
    end
    
    [Ci_sorted, idx_nodes] = sort(Ci_ref);
    Mat_sorted_all{m} = current_data(idx_nodes, idx_nodes);
    
end


%% ================= ALLÉGEANCE (subplot) =================

figure('Name','Allégeance FC vs Log-SC')

for m = 1:2
    
    subplot(1,2,m)
    imagesc(P_all{m})
    axis square
    colorbar
    
    title(['Allégeance ', modes{m}])
    
end


%% ================= MATRICES TRIÉES (subplot) =================

figure('Name','Matrices triées FC vs Log-SC')

for m = 1:2
    
    subplot(1,2,m)
    imagesc(Mat_sorted_all{m})
    axis square
    colormap(jet)
    colorbar
    
    title(['Matrice triée ', modes{m}])
    
end